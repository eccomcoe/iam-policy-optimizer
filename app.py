import json
from flask import Flask, request, render_template, jsonify
import boto3
from io import BytesIO
import re

app = Flask(__name__)

# 初始化Access Analyzer客户端
access_analyzer_client = boto3.client('accessanalyzer')

# 验证IAM Policy的函数
def validate_policy(policy):
    try:
        response = access_analyzer_client.validate_policy(
            policyDocument=json.dumps(policy),
            policyType='IDENTITY_POLICY'
        )
        findings = response.get('findings', [])
        print(findings)
        if len(findings)>0:
            return False, "\n".join([f"{finding['findingType']}: {finding['findingDetails']}" for finding in findings])
        return True, "Policy is valid."
    except Exception as e:
        return False, str(e)

# 去除空白字符以计算政策长度
def calculate_policy_length(policy):
    return len(re.sub(r'\s+', '', json.dumps(policy)))

# 将Policy按服务拆分的函数
def split_policy_by_service(policy):
    services = {}
    unchanged_statements = []

    for statement in policy['Statement']:
        if 'Action' not in statement:
            unchanged_statements.append(statement)
            continue  # 如果没有Action字段，跳过该语句

        actions = statement['Action']
        if not isinstance(actions, list):
            actions = [actions]

        for action in actions:
            service = action.split(':')[0]
            if service not in services:
                services[service] = []
            services[service].append(action)

    # 将服务按名称排序
    sorted_services = sorted(services.items(), key=lambda item: item[0])

    optimized_statements = []
    for service, actions in sorted_services:
        # 将操作按名称排序
        sorted_actions = sorted(actions)
        optimized_statements.append({
            "Sid": f"{service}Policy",
            "Effect": "Allow",
            "Action": sorted_actions,
            "Resource": statement.get('Resource', '*'),  # 使用get方法获取Resource，默认值为'*'
            "Condition": statement.get('Condition', {})  # 使用get方法获取Condition，默认值为{}
        })

    # 合并未改变的语句
    optimized_statements.extend(unchanged_statements)

    result_policy = {
        "Version": policy["Version"],
        "Statement": optimized_statements
    }

    return [result_policy]

# 将Policy按权限类型拆分的函数
def split_policy_by_permission_type(policy):
    read_actions = []
    write_actions = []
    privileged_actions = []
    unchanged_statements = []

    for statement in policy['Statement']:
        if 'Action' not in statement:
            unchanged_statements.append(statement)
            continue  # 如果没有Action字段，跳过该语句

        actions = statement['Action']
        if not isinstance(actions, list):
            actions = [actions]

        for action in actions:
            if 'Get' in action or 'List' in action or 'Describe' in action:
                read_actions.append(action)
            elif 'PassRole' in action or 'PutRolePolicy' in action or 'AttachRolePolicy' in action or 'DetachRolePolicy' in action:
                privileged_actions.append(action)
            else:
                write_actions.append(action)

    # 对每个分类的操作进行排序
    read_actions.sort()
    write_actions.sort()
    privileged_actions.sort()

    result_policy = {
        "Version": policy["Version"],
        "Statement": unchanged_statements
    }

    # 添加读操作
    if read_actions:
        result_policy["Statement"].append({
            "Sid": "ReadPolicy",
            "Effect": "Allow",
            "Action": read_actions,
            "Resource": statement.get('Resource', '*'),  # 使用get方法获取Resource，默认值为'*'
            "Condition": statement.get('Condition', {})  # 使用get方法获取Condition，默认值为{}
        })

    # 添加写操作
    if write_actions:
        result_policy["Statement"].append({
            "Sid": "WritePolicy",
            "Effect": "Allow",
            "Action": write_actions,
            "Resource": statement.get('Resource', '*'),  # 使用get方法获取Resource，默认值为'*'
            "Condition": statement.get('Condition', {})  # 使用get方法获取Condition，默认值为{}
        })

    # 添加特权操作
    if privileged_actions:
        result_policy["Statement"].append({
            "Sid": "PrivilegedPolicy",
            "Effect": "Allow",
            "Action": privileged_actions,
            "Resource": statement.get('Resource', '*'),  # 使用get方法获取Resource，默认值为'*'
            "Condition": statement.get('Condition', {})  # 使用get方法获取Condition，默认值为{}
        })

    return [result_policy]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/optimize', methods=['POST'])
def optimize():
    policy_json = request.form['policy']
    strategy = request.form['strategy']
    policyType = request.form['policyType']
    validate = request.form.get('validate') == 'on'

    print('Received policy:', policy_json)
    print('Received strategy:', strategy)
    print('Received policy type:', policyType)
    print('Validate policy:', validate)

    policy = json.loads(policy_json)

    if validate:
        is_valid, validation_message = validate_policy(policy)
        if not is_valid:
            return jsonify({"error": validation_message})

    # 设置不同Policy类型的字符限制
    if policyType == 'user':
        limit = 2048
    elif policyType == 'role':
        limit = 10240
    elif policyType == 'group':
        limit = 5120
    elif policyType == 'managed':
        limit = 6144
    else:
        return "Invalid policy type", 400

    if strategy == 'service':
        optimized_policies = split_policy_by_service(policy)
    elif strategy == 'permission':
        optimized_policies = split_policy_by_permission_type(policy)
    else:
        return "Invalid strategy", 400

    # 计算优化后的Policy长度
    optimized_policies = [{
        "Version": p["Version"],
        "Statement": [s for s in p["Statement"] if calculate_policy_length(s) <= limit]
    } for p in optimized_policies]

    # 处理超出限制的Policy
    final_policies = []
    for opt_policy in optimized_policies:
        current_policy = {
            "Version": opt_policy["Version"],
            "Statement": []
        }
        for statement in opt_policy["Statement"]:
            if calculate_policy_length(current_policy) + calculate_policy_length(statement) > limit:
                final_policies.append(current_policy)
                current_policy = {
                    "Version": opt_policy["Version"],
                    "Statement": []
                }
            current_policy["Statement"].append(statement)
        final_policies.append(current_policy)

    original_length = calculate_policy_length(policy)
    optimized_lengths = [calculate_policy_length(p) for p in final_policies]

    return jsonify({
        "original_policy": json.dumps(policy, indent=4),
        "optimized_policies": [json.dumps(p, indent=4) for p in final_policies],
        "original_length": original_length,
        "optimized_lengths": optimized_lengths
    })

if __name__ == '__main__':
    app.run(debug=True)
