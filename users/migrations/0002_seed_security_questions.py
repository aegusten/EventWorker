from django.db import migrations

def create_security_questions(apps, schema_editor):
    SecurityQuestion = apps.get_model('users', 'SecurityQuestion')

    SecurityQuestion.objects.create(
        question_text="Security Question 1",
        option1="Your first pet's name?",
        option2="Your favorite color?",
        option3="Your best friend's name?"
    )
    SecurityQuestion.objects.create(
        question_text="Security Question 2",
        option1="Your primary school?",
        option2="Your hometown?",
        option3="Your childhood nickname?"
    )
    SecurityQuestion.objects.create(
        question_text="Security Question 3",
        option1="Mother's maiden name?",
        option2="Favorite food?",
        option3="First job title?"
    )

class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_security_questions),
    ]
