# Financial Market Analysis Data Pipeline

A data pipeline...

Serverless

## Dataset

[Polygon UI](https://polygon.io/)

## Tools and Technologies

- Data Lake: Google Cloud Storage
- Transformation: Google Cloud Dataproc - Spark
- Data Warehouse: Google BigQuery
- Data Visualization:
- Orchestration: Google Composer - Airflow
- Infrastructure as Code: Terraform
- Language: Python

## Data Architecture

## Process

### Pre-requisites

[!WARNING] It's possible to be charged. Pending explanation...

[!NOTE] Skip the following steps if they are already done.

- [GCP Account and gcloud CLI installation]()
- [Terraform installation](https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli)

### Setup

- Set project ID for TF

```
terraform init
```

```
terraform plan
```

- Enter your GCP project ID

- A plan for the creation of the different resources will be shown.

- Create the resources

```
terraform apply
```

- Type `yes` to confirm.

- Destroy the infra:

```
terraform destroy
```

## Future improvements

-

## Tasks

- Analyse source data
- Prepare infra with Terraform
- Design data model
- Draw data architecture
- Finish documentation

## References

- https://medium.com/@williamwarley/a-complete-guide-to-deploy-main-services-in-gcp-with-terraform-f16f18655ca8
