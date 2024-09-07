# IAM Policy Optimizer

IAM Policy Optimizer 是一个基于 Flask 的 Web 应用程序，用于在编写AWS Identity and Access Management (IAM) 的Policy过程中Policy文档，以使其更加规整清晰，并解决Policy长度限制的问题。

## 目录

- [背景](#背景)
- [功能](#功能)
- [安装](#安装)
- [使用](#使用)
- [API 端点](#api-端点)

### 背景

#### IAM Policy 的相关限制

AWS Identity and Access Management (IAM) 是 AWS 提供的一种用于控制对 AWS 资源访问的服务。IAM Policy 是 IAM 的核心组件之一，用于定义权限和访问控制。然而，IAM Policy 存在一些限制：

1. **字符限制**：
   - User inline policy: 2048 字符
   - Role inline policy: 10240 字符
   - Group inline policy: 5120 字符
   - Customer managed policy: 6144 字符
   有时，会遇到编写的Policy文档较复杂，超出了相关字符数限制的情况，这时需要将Policy文档拆分成多个，再挂载到所需的IAM object上。

2. **复杂性**：随着系统规模的扩大和权限需求的增加，IAM Policy 变得越来越复杂，导致管理难度增加。有时我们希望对Policy进行有规律的整理，以方便管理和后续修改。

3. **维护性**：长期以来，随着需求的变化，IAM Policy 可能会变得臃肿和不一致，增加了维护的难度。

#### 为什么要进行 IAM Policy 的优化

1. **提升安全性**：优化后的 IAM Policy 可以进一步减少多余的权限，确保遵循最小权限原则，从而提升系统的安全性。

2. **提高可读性和可维护性**：简化和结构化的 Policy 更易于理解和维护，有助于减少人为错误。

3. **符合字符限制**：确保 IAM Policy 符合 AWS 的字符限制，避免由于 Policy 过长而导致的错误。

### 功能

针对IAM Policy编写过程中可能遇到的场景，IAM Policy Optimizer 提供以下功能：

- **验证 IAM Policy**：使用 AWS Access Analyzer 验证 IAM Policy 的有效性。
- **优化策略**：
  - 按服务拆分 Policy
  - 按权限类型（读/写/特权）拆分 Policy
- **Policy 长度控制**：根据不同类型的 IAM Policy 设置字符长度限制，并对超出限制的 Policy 进行拆分。
- **可下载优化后的 Policy**：用户可以下载优化后的 IAM Policy。

### 安装

1. **克隆仓库**

   ```bash
   git clone https://github.com/your_username/iam-policy-optimizer.git
   cd iam-policy-optimizer
   ```

2. **(可选)创建虚拟环境并激活**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # 对于 Windows 使用 `venv\Scripts\activate`
   ```

3. **安装依赖**

   ```bash
   pip install -r requirements.txt
   ```

4. **配置 AWS 凭证**

   确保您的 AWS 凭证配置正确，可以通过 `aws configure` 命令配置，或使用aws-vault等工具。

5. **运行应用程序**

   ```bash
   python app.py
   ```

   应用程序将在 `http://127.0.0.1:5000` 上运行。

### 使用

1. **打开浏览器并访问** `http://127.0.0.1:5000`
2. **粘贴 IAM Policy JSON** 到文本框中。
3. **选择优化策略**：
   - 按服务拆分
   - 按权限类型（读/写）拆分
4. **选择 IAM Policy 类型**：
   - User inline（2048 字符）
   - Role inline（10240 字符）
   - Group inline（5120 字符）
   - Customer managed（6144 字符）
5. **点击优化按钮**。
6. **查看优化结果**，并下载优化后的 IAM Policy。

### API 端点

#### `POST /optimize`

优化 IAM Policy。

**请求参数**：

- `policy`：IAM Policy JSON 字符串
- `strategy`：优化策略（`service` 或 `permission`）
- `policyType`：IAM Policy 类型（`user`、`role`、`group`、`managed`）

**响应**：

返回优化后的 IAM Policy 及其长度信息。