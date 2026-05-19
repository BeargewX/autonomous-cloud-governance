resource "aws_iam_role_policy" "ec2_describe" {
  name = "${var.project_name}-ec2-describe-policy"
  role = aws_iam_role.ec2_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "ec2:DescribeInstances",
        "ec2:DescribeInstanceStatus"
      ]
      Resource = "*"
    }]
  })
}