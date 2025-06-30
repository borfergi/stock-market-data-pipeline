# Stock Market Analysis Data Pipeline

A fully serverless data pipeline that centralizes and prepares stock market data from your selected companies. It's based on a modern and scalable data architecture for ingesting, transforming, and analyzing stock market data using GCS, PySpark, BigQuery, Composer (Airflow), and Terraform.

Data source extraction is automated for daily retrieval of stock price information from the [Polygon.io API](https://polygon.io/). Then, it is processed and modeled using PySpark and loaded into a modern data warehouse with a dimensional model for analytics and visualization.

The architecture is based on Google Cloud Services and deployed using Terraform as IaC.

## Dataset

[Polygon API](https://polygon.io/) provides a free tier for this kind of project. There exist some limitations but we can to extract the previous day stock price of 5 companies every minute.

By default we are fetching data from MAANG companies, but you can provide your preferred companies introducing its symbol when it is asked to.

## Tools and Technologies

- Google Cloud Storage -> Data lake to store the data files in two layers: Raw and Processed with Parquet files.
- Dataproc Serverless (PySpark) -> Handles data transformation and formatting into a dimensional model.
- Google BigQuery as analytical data warehouse and dashboard backend.
- Google Composer (Airflow) -> Orchestrates the end-to-end data workflow on a daily schedule.
- Terraform: Manages infrastructure as code to deploy all cloud resources.

## Data Architecture

**Tech Architecture**

-- Future image --

**Dimensional Model**

-- Future image --

- fact_stock_price:
- dim_company:
- dim_exchange:
- dim_date:

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

MAANG companies. If you want to analize other companes, change the symbols...

```
terraform init
```

```
terraform plan
```

- A plan for the creation of the different resources will be shown.

> [!NOTE]
> While it's possible to create a Dataproc cluster manually, this project takes advantage of Airflow to automate the entire process: from provisioning the Dataproc cluster, running the PySpark job, to automatically delete the cluster once the job is complete.

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

## Future improvements

- Create dashboard for visualization
- Implement more data validation checks
- Add logging and alerts
- Automate pipeline deployment with CI/CD

## References

- https://medium.com/@williamwarley/a-complete-guide-to-deploy-main-services-in-gcp-with-terraform-f16f18655ca8
