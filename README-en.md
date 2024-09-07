# IAM Policy Optimizer

IAM Policy Optimizer is a Flask-based web application designed to organize and optimize AWS Identity and Access Management (IAM) policies, making them clearer and addressing policy length limitations.

## Table of Contents

- [Background](#background)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)

### Background

#### Limitations of IAM Policies

AWS Identity and Access Management (IAM) is a service provided by AWS to control access to AWS resources. IAM Policy is one of the core components of IAM, used to define permissions and access control. However, IAM Policies have some limitations:

1. **Character Limits**:
   - User inline policy: 2048 characters
   - Role inline policy: 10240 characters
   - Group inline policy: 5120 characters
   - Customer managed policy: 6144 characters
   Sometimes, the policy documents we write are complex and exceed these character limits, requiring us to split the policy into multiple documents and attach them to the necessary IAM objects.

2. **Complexity**: As the system scales and permission requirements increase, IAM Policies become more complex, making management difficult. Sometimes we want to organize policies systematically to facilitate management and future modifications.

3. **Maintainability**: Over time, as requirements change, IAM Policies can become bloated and inconsistent, increasing the difficulty of maintenance.

#### Why Optimize IAM Policies

1. **Enhance Security**: Optimized IAM Policies can further reduce excessive permissions, ensuring adherence to the principle of least privilege, thereby enhancing system security.

2. **Improve Readability and Maintainability**: Simplified and structured policies are easier to understand and maintain, helping to reduce human errors.

3. **Meet Character Limits**: Ensure IAM Policies comply with AWS's character limits, avoiding errors caused by overly long policies.

### Features

IAM Policy Optimizer provides the following features for scenarios encountered during IAM policy writing:

- **Validate IAM Policies**: Use AWS Access Analyzer to validate the effectiveness of IAM policies.
- **Optimize Policies**:
  - Split policies by service
  - Split policies by permission type (read/write/privilege)
- **Policy Length Control**: Set character length limits for different types of IAM policies and split policies that exceed the limits.
- **Download Optimized Policies**: Users can download the optimized IAM policies.

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/your_username/iam-policy-optimizer.git
   cd iam-policy-optimizer
   ```

2. **(Optional) Create and activate a virtual environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # For Windows, use `venv\Scripts\activate`
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure AWS credentials**

   Ensure your AWS credentials are configured correctly. You can configure them using the `aws configure` command or tools like aws-vault.

5. **Run the application**

   ```bash
   python app.py
   ```

   The application will run at `http://127.0.0.1:5000`.

### Usage

1. **Open a browser and visit** `http://127.0.0.1:5000`
2. **Paste the IAM Policy JSON** into the text box.
3. **Select an optimization strategy**:
   - Split by service
   - Split by permission type (read/write)
4. **Select the IAM Policy type**:
   - User inline (2048 characters)
   - Role inline (10240 characters)
   - Group inline (5120 characters)
   - Customer managed (6144 characters)
5. **Click the optimize button**.
6. **View the optimized results** and download the optimized IAM policies.

### API Endpoints

#### `POST /optimize`

Optimize IAM Policies.

**Request Parameters**:

- `policy`: IAM Policy JSON string
- `strategy`: Optimization strategy (`service` or `permission`)
- `policyType`: IAM Policy type (`user`, `role`, `group`, `managed`)

**Response**:

Returns the optimized IAM Policy and its length information.