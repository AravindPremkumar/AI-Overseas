import os
import django
import pandas as pd
from decimal import Decimal

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from students.models import University

def populate_universities():
    csv_path = 'AI/university_dataset_80_rows.csv'
    if not os.path.exists(csv_path):
        print(f"CSV not found at {csv_path}")
        return

    df = pd.read_csv(csv_path)
    
    # Track statistics
    created_count = 0
    updated_count = 0

    for _, row in df.iterrows():
        # Mapping CSV columns to model fields
        # Note: headers in CSV are University_Name,Country,Course_Field,Degree_Level,Min_IELTS,Min_German_Score,Min_Academic_Percentage,Tuition_Fee_USD,Backlogs_Allowed,Work_Experience_Required,Intake,Ranking_Tier
        
        # Check if university entry already exists to avoid duplicates
        uni, created = University.objects.get_or_create(
            name=row['University_Name'],
            country=row['Country'],
            course_field=row['Course_Field'],
            degree_level=row['Degree_Level'],
            defaults={
                'min_ielts': float(row['Min_IELTS']),
                'min_german_score': float(row['Min_German_Score']),
                'min_academic_percentage': float(row['Min_Academic_Percentage']),
                'tuition_fee_usd': Decimal(str(row['Tuition_Fee_USD'])),
                'backlogs_allowed': int(row['Backlogs_Allowed']),
                'work_experience_required': int(row['Work_Experience_Required']),
                'intake': row['Intake'],
                'ranking_tier': row['Ranking_Tier'],
            }
        )
        
        if created:
            created_count += 1
        else:
            # Optionally update if it already exists
            uni.min_ielts = float(row['Min_IELTS'])
            uni.min_german_score = float(row['Min_German_Score'])
            uni.min_academic_percentage = float(row['Min_Academic_Percentage'])
            uni.tuition_fee_usd = Decimal(str(row['Tuition_Fee_USD']))
            uni.backlogs_allowed = int(row['Backlogs_Allowed'])
            uni.work_experience_required = int(row['Work_Experience_Required'])
            uni.intake = row['Intake']
            uni.ranking_tier = row['Ranking_Tier']
            uni.save()
            updated_count += 1

    print(f"Population complete. Created: {created_count}, Updated: {updated_count}")

if __name__ == '__main__':
    populate_universities()
