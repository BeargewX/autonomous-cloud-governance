# Terraform Notes

This directory is configured for HCP Terraform.

## Commands

```powershell
terraform init
terraform plan
terraform apply
terraform output
```

## Remote Backend

The root module uses:

```hcl
cloud {
  organization = "cloud-governance-beargewx"
  workspaces {
    name = "autonomous-cloud-governance"
  }
}
```

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
