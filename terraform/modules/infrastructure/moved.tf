moved {
  from = aws_eip.app
  to   = aws_eip.app[0]
}

moved {
  from = aws_cloudwatch_log_group.vpc_flow_logs
  to   = aws_cloudwatch_log_group.vpc_flow_logs[0]
}

moved {
  from = aws_iam_role.vpc_flow_logs
  to   = aws_iam_role.vpc_flow_logs[0]
}

moved {
  from = aws_iam_role_policy.vpc_flow_logs
  to   = aws_iam_role_policy.vpc_flow_logs[0]
}

moved {
  from = aws_flow_log.main
  to   = aws_flow_log.main[0]
}
