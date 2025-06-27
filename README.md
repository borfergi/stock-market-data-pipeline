# Stock Market Analysis Data Pipeline

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

-- Future image --

## Process

### Pre-requisites

> [!WARNING]
> It's possible to be charged. Pending explanation...

> [!NOTE]
> Skip the following steps if they are already done.

- [GCP Account and gcloud CLI installation]()
- [Terraform installation](https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli)
- Follow the steps to [set up GCP](setup/gcp_setup.md)
- Polygon API ....

### Setup

- Set project ID, service_account, and polygon key in infra/variables.tf file

```
terraform init
```

```
terraform plan
```

- A plan for the creation of the different resources will be shown.

- Create the resources

```
terraform apply
```

- The environment could take XX minutes to be completely deployed

- Type `yes` to confirm.

- Upload manually erp_companies.csv file to activate the Composer
  gsutil cp erp_companies.csv gs://datalake-stock-market-bucket/raw

```
gsutils ...
```

- Destroy the infra:

```
cd infra/
terraform destroy
```

One can always create a Dataproc cluster manually. However, in this project, we will leverage the power of airflow to create the Dataproc cluster, submit the PySpark job, and then again delete the Dataproc after finishing the job.

## Future improvements

- Create VPC....

## References

- https://medium.com/@williamwarley/a-complete-guide-to-deploy-main-services-in-gcp-with-terraform-f16f18655ca8
