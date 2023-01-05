
# To update this
# - fiddle with the dashboard in the AWS console
# - Actions -> View/Edit Source
# - replace the prefix (DeathDice) with ${var.name}
# - replace the prefix (DeathDiceAnalytics) with ${var.name_analytics}
# - replace the project name (Death Dice) with ${var.project}
resource "aws_cloudwatch_dashboard" "dashboard" {
  dashboard_name = var.name
  dashboard_body = jsonencode(
{
    "widgets": [
        {
            "height": 6,
            "width": 6,
            "y": 0,
            "x": 12,
            "type": "metric",
            "properties": {
                "metrics": [
                    [ { "expression": "RUNNING_SUM(m1+m3)", "id": "e1", "label": "Cumulative ReadCapacityUnits", "region": "ap-southeast-2" } ],
                    [ { "expression": "RUNNING_SUM(m2+m4)", "id": "e2", "label": "Cumulative WriteCapacityUnits", "region": "ap-southeast-2" } ],
                    [ "AWS/DynamoDB", "ConsumedReadCapacityUnits", "TableName", "${var.name}", { "id": "m1", "visible": false } ],
                    [ ".", "ConsumedWriteCapacityUnits", ".", ".", { "id": "m2", "visible": false } ],
                    [ ".", "ConsumedReadCapacityUnits", ".", "${var.name_analytics}", { "id": "m3", "visible": false } ],
                    [ ".", "ConsumedWriteCapacityUnits", ".", ".", { "id": "m4", "visible": false } ]
                ],
                "annotations": {
                    "horizontal": [
                        {
                            "color": "#ff7f0e",
                            "label": "1c of writes",
                            "value": 7027
                        },
                        {
                            "color": "#1f77b4",
                            "label": "1c of reads",
                            "value": 35137
                        }
                    ]
                },
                "period": 300,
                "region": "ap-southeast-2",
                "stacked": false,
                "stat": "Sum",
                "title": "DynamoDB Costs",
                "view": "timeSeries",
                "yAxis": {
                    "left": {
                        "min": 0,
                        "showUnits": false
                    },
                    "right": {
                        "showUnits": false
                    }
                }
            }
        },
        {
            "height": 13,
            "width": 12,
            "y": 0,
            "x": 0,
            "type": "explorer",
            "properties": {
                "labels": [
                    {
                        "key": "Project",
                        "value": "${var.project}"
                    }
                ],
                "metrics": [
                    {
                        "metricName": "Duration",
                        "resourceType": "AWS::Lambda::Function",
                        "stat": "p90"
                    },
                    {
                        "metricName": "Errors",
                        "resourceType": "AWS::Lambda::Function",
                        "stat": "Sum"
                    },
                    {
                        "metricName": "Invocations",
                        "resourceType": "AWS::Lambda::Function",
                        "stat": "Sum"
                    },
                    {
                        "metricName": "Throttles",
                        "resourceType": "AWS::Lambda::Function",
                        "stat": "Sum"
                    }
                ],
                "period": 300,
                "region": "ap-southeast-2",
                "splitBy": "Project",
                "title": "Lambda",
                "widgetOptions": {
                    "legend": {
                        "position": "bottom"
                    },
                    "rowsPerPage": 2,
                    "stacked": false,
                    "view": "timeSeries",
                    "widgetsPerRow": 2
                }
            }
        },
        {
            "height": 6,
            "width": 6,
            "y": 6,
            "x": 12,
            "type": "metric",
            "properties": {
                "annotations": {
                    "horizontal": [
                        {
                            "color": "#1f77b4",
                            "label": "1c of requests",
                            "value": 7693
                        }
                    ]
                },
                "metrics": [
                    [ { "expression": "RUNNING_SUM(m1)", "id": "e1", "label": "Cumulative Message Count", "region": "ap-southeast-2" } ],
                    [ "AWS/ApiGateway", "MessageCount", "Stage", "production", "ApiId", "fd7yv03sm1", { "id": "m1", "visible": false } ]
                ],
                "period": 86400,
                "region": "ap-southeast-2",
                "stacked": false,
                "stat": "Sum",
                "title": "ApiGateway Costs",
                "view": "timeSeries",
                "yAxis": {
                    "left": {
                        "min": 0
                    }
                }
            }
        },
        {
            "height": 6,
            "width": 6,
            "y": 0,
            "x": 18,
            "type": "metric",
            "properties": {
                "metrics": [
                    [ { "expression": "RUNNING_SUM(m1+m2+m3+m4+m5+m6+m7+m8+m9+m10+m11)", "id": "e1", "label": "Cumulative Processing Time", "region": "ap-southeast-2" } ],
                    [ "AWS/Lambda", "Duration", "FunctionName", "${var.name}-Connect", "Resource", "${var.name}-Connect", { "id": "m1", "visible": false } ],
                    [ "...", "${var.name}-CreateGame", ".", "${var.name}-CreateGame", { "id": "m2", "visible": false } ],
                    [ "...", "${var.name}-Disconnect", ".", "${var.name}-Disconnect", { "id": "m3", "visible": false } ],
                    [ "...", "${var.name}-JoinGame", ".", "${var.name}-JoinGame", { "id": "m4", "visible": false } ],
                    [ "...", "${var.name}-NewRound", ".", "${var.name}-NewRound", { "id": "m5", "visible": false } ],
                    [ "...", "${var.name}-RollDice", ".", "${var.name}-RollDice", { "id": "m6", "visible": false } ],
                    [ "...", "${var.name}-SetNickname", ".", "${var.name}-SetNickname", { "id": "m7", "visible": false } ],
                    [ ".", ".", ".", "${var.name}-ExtractAndTransform", { "id": "m8", "visible": false } ],
                    [ "...", "${var.name_analytics}-CacheResult", { "id": "m9", "visible": false } ],
                    [ "...", "${var.name_analytics}-GetStatistics", { "id": "m10", "visible": false } ],
                    [ "...", "${var.name_analytics}-StartQuery", { "id": "m11", "visible": false } ]
                ],
                "annotations": {
                    "horizontal": [
                        {
                            "color": "#1f77b4",
                            "label": "1c of 128MB",
                            "value": 4761905
                        }
                    ]
                },
                "period": 300,
                "region": "ap-southeast-2",
                "stacked": false,
                "stat": "Sum",
                "title": "Lambda Costs",
                "view": "timeSeries",
                "yAxis": {
                    "left": {
                        "min": 0
                    }
                }
            }
        },
        {
            "height": 6,
            "width": 6,
            "y": 6,
            "x": 18,
            "type": "metric",
            "properties": {
                "metrics": [
                    [ { "expression": "RUNNING_SUM(m1) / (1024^2)", "label": "Cumulative Processed MB", "id": "e1" } ],
                    [ "AWS/Athena", "ProcessedBytes", "WorkGroup", "${var.name_analytics}", { "id": "m1", "visible": false } ]
                ],
                "annotations": {
                    "horizontal": [
                        {
                            "label": "1c of s3 objects",
                            "value": 2097
                        }
                    ]
                },
                "period": 300,
                "region": "ap-southeast-2",
                "stacked": false,
                "stat": "Sum",
                "title": "Athena Costs",
                "view": "timeSeries",
                "yAxis": {
                    "left": {
                        "min": 0
                    }
                }
            }
        }
    ]
}
  )
}
