###############################################################################
# SAM - SageMaker Batch Transform prerequisites (Role + Model)
###############################################################################

locals {
  sam_batch_model_name = format(
    "%s-%s-%s-xxxx-doc-processing-model",
    local.entity,
    local.project,
    local.environment
  )

  # Buckets names based on your S3 naming convention (same as module "buckets")
  sam_raw_bucket_name = format("%s-%s-%s-xxxx-%s", local.entity, local.project, local.environment, "raw-document")
  sam_output_bucket_name = format("%s-%s-%s-xxxx-%s", local.entity, local.project, local.environment, "output-document")
}

data "aws_iam_policy_document" "sam_sagemaker_assume" {
  statement {
    effect = "Allow"
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["sagemaker.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "sam_sagemaker_batch_transform_role" {
  name               = "${local.sam_batch_model_name}-role"
  assume_role_policy = data.aws_iam_policy_document.sam_sagemaker_assume.json

  tags = merge(local.xxxx_base_tags, {
    Name = "${local.sam_batch_model_name}-role"
  })
}

data "aws_iam_policy_document" "sam_sagemaker_batch_transform_policy" {
  # S3 input/output
  statement {
    effect = "Allow"
    actions = [
      "s3:ListBucket",
      "s3:GetBucketLocation"
    ]
    resources = [
      "arn:aws:s3:::${local.sam_raw_bucket_name}",
      "arn:aws:s3:::${local.sam_enriched_bucket_name}"
    ]
  }

  statement {
    effect = "Allow"
    actions = [
      "s3:GetObject",
      "s3:PutObject",
      "s3:DeleteObject"
    ]
    resources = [
      "arn:aws:s3:::${local.sam_raw_bucket_name}/*",
      "arn:aws:s3:::${local.sam_enriched_bucket_name}/*"
    ]
  }

  # KMS (because your buckets are SSE-KMS)
  statement {
    effect = "Allow"
    actions = [
      "kms:Encrypt",
      "kms:Decrypt",
      "kms:GenerateDataKey",
      "kms:DescribeKey"
    ]
    resources = [aws_kms_alias.xxxx_kms_key_alias.target_key_arn]
  }

  # ECR pull permissions (SageMaker needs to pull your image)
  statement {
    effect = "Allow"
    actions = [
      "ecr:GetAuthorizationToken",
      "ecr:BatchGetImage",
      "ecr:GetDownloadUrlForLayer"
    ]
    resources = ["*"]
  }

  # CloudWatch Logs (optional but recommended)
  statement {
    effect = "Allow"
    actions = [
      "logs:CreateLogStream",
      "logs:PutLogEvents",
      "logs:CreateLogGroup",
      "logs:DescribeLogStreams"
    ]
    resources = ["*"]
  }
}

resource "aws_iam_policy" "sam_sagemaker_batch_transform_policy" {
  name   = "${local.sam_batch_model_name}-policy"
  policy = data.aws_iam_policy_document.sam_sagemaker_batch_transform_policy.json

  tags = merge(local.xxxx_base_tags, {
    Name = "${local.sam_batch_model_name}-policy"
  })
}

resource "aws_iam_role_policy_attachment" "sam_sagemaker_batch_transform_attach" {
  role       = aws_iam_role.sam_sagemaker_batch_transform_role.name
  policy_arn = aws_iam_policy.sam_sagemaker_batch_transform_policy.arn
}

resource "aws_sagemaker_model" "sam_doc_processing_model" {
  name               = local.sam_batch_model_name
  execution_role_arn = aws_iam_role.sam_sagemaker_batch_transform_role.arn

  primary_container {
    image = var.sam_doc_processing_image_uri
  }

  tags = merge(local.xxxx_base_tags, {
    Name = local.sam_batch_model_name
  })
}
