
# To update this
# - fiddle with the dashboard in the AWS console
# - Actions -> View/Edit Source
# - replace the prefix (DeathDice) with ${var.name}
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
                "metrics": [
                    [ { "expression": "RUNNING_SUM(m1)", "id": "e1", "label": "Cumulative ReadCapacityUnits", "region": "ap-southeast-2" } ],
                    [ { "expression": "RUNNING_SUM(m2)", "id": "e2", "label": "Cumulative WriteCapacityUnits", "region": "ap-southeast-2" } ],
                    [ "AWS/DynamoDB", "ConsumedReadCapacityUnits", "TableName", "${var.name}", { "id": "m1", "visible": false } ],
                    [ ".", "ConsumedWriteCapacityUnits", ".", ".", { "id": "m2", "visible": false } ]
                ],
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
                "annotations": {
                    "horizontal": [
                        {
                            "color": "#1f77b4",
                            "label": "1c of 128MB",
                            "value": 4761905
                        }
                    ]
                },
                "metrics": [
                    [ { "expression": "RUNNING_SUM(m1+m2+m3+m4+m5+m6+m7)", "id": "e1", "label": "Cumulative Processing Time", "region": "ap-southeast-2" } ],
                    [ "AWS/Lambda", "Duration", "FunctionName", "${var.name}-Connect", "Resource", "${var.name}-Connect", { "id": "m1", "visible": false } ],
                    [ "...", "${var.name}-CreateGame", ".", "${var.name}-CreateGame", { "id": "m2", "visible": false } ],
                    [ "...", "${var.name}-Disconnect", ".", "${var.name}-Disconnect", { "id": "m3", "visible": false } ],
                    [ "...", "${var.name}-JoinGame", ".", "${var.name}-JoinGame", { "id": "m4", "visible": false } ],
                    [ "...", "${var.name}-NewRound", ".", "${var.name}-NewRound", { "id": "m5", "visible": false } ],
                    [ "...", "${var.name}-RollDice", ".", "${var.name}-RollDice", { "id": "m6", "visible": false } ],
                    [ "...", "${var.name}-SetNickname", ".", "${var.name}-SetNickname", { "id": "m7", "visible": false } ]
                ],
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
                    [ { "expression": "RUNNING_SUM(m1)", "label": "Cumulative IncomingBytes", "id": "e1", "region": "ap-southeast-2" } ],
                    [ "AWS/Kinesis", "IncomingBytes", "StreamName", "${var.name}", { "label": "IncomingBytes", "id": "m1", "stat": "Sum" } ]
                ],
                "view": "timeSeries",
                "stacked": false,
                "region": "ap-southeast-2",
                "annotations": {
                    "horizontal": [
                        {
                            "label": "1c of ingest",
                            "value": 290000000
                        }
                    ]
                },
                "period": 300,
                "stat": "Average",
                "title": "Kinesis Data Stream"
            }
        },
        {
            "height": 6,
            "width": 6,
            "y": 12,
            "x": 12,
            "type": "metric",
            "properties": {
                "metrics": [
                    [ { "expression": "RUNNING_SUM(m1)", "label": "Cumulative S3 Object Count", "id": "e1", "region": "ap-southeast-2" } ],
                    [ "AWS/Firehose", "DeliveryToS3.ObjectCount", "DeliveryStreamName", "${var.name}", { "id": "m1", "visible": false } ]
                ],
                "view": "timeSeries",
                "stacked": false,
                "region": "ap-southeast-2",
                "title": "Kinesis Firehose - s3 objects",
                "stat": "Sum",
                "period": 300,
                "annotations": {
                    "horizontal": [
                        {
                            "label": "1c of s3 objects",
                            "value": 1587
                        }
                    ]
                },
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
            "y": 12,
            "x": 18,
            "type": "metric",
            "properties": {
                "metrics": [
                    [ { "expression": "RUNNING_SUM(m2)", "label": "Cumulative S3 Bytes", "id": "e2", "region": "ap-southeast-2" } ],
                    [ "AWS/Firehose", "DeliveryToS3.Bytes", "DeliveryStreamName", "${var.name}", { "id": "m2", "visible": false } ]
                ],
                "view": "timeSeries",
                "stacked": false,
                "region": "ap-southeast-2",
                "title": "Kinesis Firehose - s3 bytes",
                "stat": "Sum",
                "period": 300,
                "annotations": {
                    "horizontal": [
                        {
                            "label": "1c of GB delivered",
                            "value": 429000000
                        }
                    ]
                },
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
