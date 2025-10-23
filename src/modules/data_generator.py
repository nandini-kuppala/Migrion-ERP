"""Synthetic data generation for demo companies."""
import random
from datetime import datetime, timedelta
from typing import Dict, List
import pandas as pd
import numpy as np
from faker import Faker

fake = Faker()
Faker.seed(42)
random.seed(42)
np.random.seed(42)


class OrangeLeagueDataGenerator:
    """Generate realistic synthetic data for Orange League Ventures Technologies."""

    def __init__(self, num_customers=5000, num_projects=1200, num_invoices=3500):
        self.num_customers = num_customers
        self.num_projects = num_projects
        self.num_invoices = num_invoices
        self.start_date = datetime(2020, 1, 1)
        self.end_date = datetime(2024, 12, 31)

    def generate_customers(self) -> pd.DataFrame:
        """Generate customer data."""
        data = []

        for i in range(self.num_customers):
            # Introduce controlled anomalies
            missing_email = random.random() < 0.10  # 10% missing emails
            duplicate = random.random() < 0.05  # 5% duplicates
            incorrect_country = random.random() < 0.03  # 3% incorrect country codes

            customer_id = i + 1 if not duplicate else random.randint(1, i) if i > 0 else 1
            company_name = fake.company()

            data.append({
                'customer_id': customer_id,
                'company_name': company_name,
                'contact_name': fake.name(),
                'email': None if missing_email else fake.company_email(),
                'phone': fake.phone_number(),
                'address': fake.street_address(),
                'city': fake.city(),
                'state': fake.state_abbr(),
                'zip_code': fake.zipcode(),
                'country': 'XX' if incorrect_country else fake.country_code(),
                'industry': random.choice([
                    'Technology', 'Finance', 'Healthcare', 'Retail',
                    'Manufacturing', 'Education', 'Government', 'Other'
                ]),
                'company_size': random.choice(['1-50', '51-200', '201-500', '501-1000', '1000+']),
                'created_date': fake.date_between(start_date=self.start_date, end_date=self.end_date),
                'status': random.choice(['Active', 'Inactive', 'Prospect', 'Churned']),
                'lifetime_value': round(random.uniform(5000, 500000), 2),
                'credit_limit': round(random.uniform(10000, 1000000), 2),
                'payment_terms': random.choice(['Net 15', 'Net 30', 'Net 45', 'Net 60']),
                'account_manager': fake.name()
            })

        return pd.DataFrame(data)

    def generate_projects(self, customers_df: pd.DataFrame) -> pd.DataFrame:
        """Generate project data."""
        data = []
        project_types = ['Web Development', 'Mobile App', 'API Integration',
                        'Cloud Migration', 'Data Analytics', 'Custom Software']
        statuses = ['Planning', 'In Progress', 'Testing', 'Completed', 'On Hold', 'Cancelled']

        for i in range(self.num_projects):
            customer_id = random.choice(customers_df['customer_id'].values)
            start_date = fake.date_between(start_date=self.start_date, end_date=self.end_date)
            duration_days = random.randint(30, 365)
            end_date = start_date + timedelta(days=duration_days)

            # Some date format inconsistencies
            if random.random() < 0.05:
                start_date = start_date.strftime('%m-%d-%Y')  # Different format
            else:
                start_date = start_date.strftime('%Y-%m-%d')

            if random.random() < 0.05:
                end_date = end_date.strftime('%d/%m/%Y')  # Another format
            else:
                end_date = end_date.strftime('%Y-%m-%d')

            data.append({
                'project_id': f'PRJ-{i+1:05d}',
                'customer_id': customer_id,
                'project_name': f"{random.choice(project_types)} for {fake.company()}",
                'project_type': random.choice(project_types),
                'description': fake.text(max_nb_chars=200),
                'start_date': start_date,
                'end_date': end_date,
                'estimated_hours': random.randint(100, 5000),
                'actual_hours': random.randint(80, 5500),
                'budget': round(random.uniform(50000, 1000000), 2),
                'actual_cost': round(random.uniform(45000, 1100000), 2),
                'status': random.choice(statuses),
                'priority': random.choice(['Low', 'Medium', 'High', 'Critical']),
                'project_manager': fake.name(),
                'team_size': random.randint(2, 15),
                'completion_percentage': random.randint(0, 100)
            })

        return pd.DataFrame(data)

    def generate_invoices(self, customers_df: pd.DataFrame, projects_df: pd.DataFrame) -> pd.DataFrame:
        """Generate invoice data."""
        data = []
        payment_methods = ['Credit Card', 'Bank Transfer', 'PayPal', 'Check', 'Wire Transfer']
        invoice_statuses = ['Draft', 'Sent', 'Paid', 'Overdue', 'Cancelled']

        for i in range(self.num_invoices):
            customer_id = random.choice(customers_df['customer_id'].values)
            project_id = random.choice(projects_df['project_id'].values) if random.random() > 0.1 else None

            invoice_date = fake.date_between(start_date=self.start_date, end_date=self.end_date)
            due_date = invoice_date + timedelta(days=random.choice([15, 30, 45, 60]))

            subtotal = round(random.uniform(5000, 200000), 2)
            tax_rate = 0.08
            tax_amount = round(subtotal * tax_rate, 2)
            total = subtotal + tax_amount

            status = random.choice(invoice_statuses)
            payment_date = None
            if status == 'Paid':
                payment_date = due_date + timedelta(days=random.randint(-10, 5))

            data.append({
                'invoice_id': f'INV-{i+1:06d}',
                'customer_id': customer_id,
                'project_id': project_id,
                'invoice_date': invoice_date.strftime('%Y-%m-%d'),
                'due_date': due_date.strftime('%Y-%m-%d'),
                'payment_date': payment_date.strftime('%Y-%m-%d') if payment_date else None,
                'subtotal': subtotal,
                'tax_rate': tax_rate,
                'tax_amount': tax_amount,
                'total': total,
                'currency': 'USD',
                'status': status,
                'payment_method': random.choice(payment_methods) if status == 'Paid' else None,
                'notes': fake.sentence() if random.random() > 0.7 else None,
                'terms': random.choice(['Net 15', 'Net 30', 'Net 45', 'Net 60'])
            })

        return pd.DataFrame(data)

    def generate_users(self) -> pd.DataFrame:
        """Generate user/employee data."""
        data = []
        departments = ['Engineering', 'Sales', 'Marketing', 'Finance', 'HR', 'Operations']
        roles = ['Developer', 'Manager', 'Analyst', 'Director', 'Executive', 'Specialist']

        for i in range(250):
            hire_date = fake.date_between(start_date=self.start_date, end_date=self.end_date)

            # Some PII data for compliance checking
            data.append({
                'user_id': f'USR-{i+1:04d}',
                'username': fake.user_name(),
                'email': fake.email(),  # PII
                'first_name': fake.first_name(),
                'last_name': fake.last_name(),
                'full_name': fake.name(),
                'phone': fake.phone_number(),  # PII
                'date_of_birth': fake.date_of_birth(minimum_age=22, maximum_age=65),  # PII
                'ssn': fake.ssn() if random.random() > 0.9 else None,  # PII - mostly missing
                'department': random.choice(departments),
                'role': random.choice(roles),
                'hire_date': hire_date.strftime('%Y-%m-%d'),
                'salary': round(random.uniform(50000, 200000), 2),  # PII
                'is_active': random.choice([True, True, True, False]),  # 75% active
                'reports_to': f'USR-{random.randint(1, i):04d}' if i > 0 else None
            })

        return pd.DataFrame(data)

    def generate_products(self) -> pd.DataFrame:
        """Generate product/service catalog data."""
        data = []
        categories = ['Software Development', 'Consulting', 'Training', 'Support', 'Licensing']
        billing_types = ['One-time', 'Monthly', 'Yearly', 'Hourly']

        for i in range(150):
            data.append({
                'product_id': f'PROD-{i+1:04d}',
                'product_name': f"{fake.catch_phrase()} {random.choice(['Service', 'Package', 'Solution'])}",
                'category': random.choice(categories),
                'description': fake.text(max_nb_chars=150),
                'unit_price': round(random.uniform(100, 50000), 2),
                'cost': round(random.uniform(50, 30000), 2),
                'billing_type': random.choice(billing_types),
                'is_active': random.choice([True, True, True, False]),
                'created_date': fake.date_between(start_date=self.start_date, end_date=self.end_date).strftime('%Y-%m-%d')
            })

        return pd.DataFrame(data)

    def generate_all(self) -> Dict[str, pd.DataFrame]:
        """Generate all datasets."""
        customers = self.generate_customers()
        projects = self.generate_projects(customers)
        invoices = self.generate_invoices(customers, projects)
        users = self.generate_users()
        products = self.generate_products()

        return {
            'customers': customers,
            'projects': projects,
            'invoices': invoices,
            'users': users,
            'products': products
        }


def generate_orange_league_data() -> Dict[str, pd.DataFrame]:
    """Main function to generate Orange League data."""
    generator = OrangeLeagueDataGenerator(
        num_customers=5000,
        num_projects=1200,
        num_invoices=3500
    )
    return generator.generate_all()


def save_datasets(datasets: Dict[str, pd.DataFrame], output_dir: str):
    """Save datasets to CSV files."""
    from pathlib import Path

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    for name, df in datasets.items():
        filepath = output_path / f"{name}.csv"
        df.to_csv(filepath, index=False)
        print(f"Saved {name}: {len(df)} rows to {filepath}")


if __name__ == "__main__":
    # Generate and save data
    datasets = generate_orange_league_data()

    # Save to data/examples/orange_league/
    from pathlib import Path
    output_dir = Path(__file__).parent.parent.parent / "data" / "examples" / "orange_league"
    save_datasets(datasets, str(output_dir))

    # Print summary
    print("\nData Generation Summary:")
    for name, df in datasets.items():
        print(f"\n{name.upper()}:")
        print(f"  Rows: {len(df)}")
        print(f"  Columns: {len(df.columns)}")
        print(f"  Missing values: {df.isnull().sum().sum()}")
        print(f"  Duplicates: {df.duplicated().sum()}")
