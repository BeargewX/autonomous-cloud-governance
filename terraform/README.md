# Terraform Notes

This directory is configured for HCP Terraform.

## Normal Demo Commands

```powershell
terraform init
terraform plan
terraform apply
terraform output
```

## Remote Backend

The root module uses HCP Terraform:

```hcl
cloud {
  organization = "cloud-governance-beargewx"
  workspaces {
    name = "autonomous-cloud-governance"
  }
}
```

## Free-First Variables

| Variable | Default | Why it matters |
|---|---:|---|
| `enable_public_ipv4` | `true` | Keeps the existing live demo endpoint working. Set false after demos to reduce public IPv4 cost. |
| `enable_public_ssh` | `false` | Prefer SSM Session Manager over internet SSH. |
| `enable_vpc_flow_logs` | `true` | Useful for governance demos, but can create CloudWatch Logs cost. |
| `ec2_cpu_credits` | `standard` | Avoids T3 unlimited burst charges. |

Review the low-cost example:

```powershell
terraform plan -var-file=free.tfvars.example
```

Do not apply it blindly. It can remove the public endpoint.

## Lambda Packaging

The infrastructure module uses the `archive_file` provider for some Lambda packages. Terraform Cloud runs from the repository checkout, so source files must exist inside the module path.

Required files:

```text
modules/infrastructure/lambda/cost_anomaly.py
modules/infrastructure/lambda/s3_lifecycle.py
```

If either file is missing, remote plan/apply fails with:

```text
could not archive missing file
```

## Common Warning

If Terraform Cloud shows this warning:

```text
Value for undeclared variable "db_password"
```

remove `db_password` from the HCP Terraform workspace variables unless you intentionally add database resources that need it.
