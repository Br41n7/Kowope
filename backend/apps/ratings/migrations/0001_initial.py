import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('orders', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('overall_score', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('dimensions', models.JSONField(default=dict)),
                ('comment', models.TextField(blank=True, max_length=2000)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('purchase_order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ratings', to='orders.purchaseorder')),
                ('reviewed', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='ratings_received', to=settings.AUTH_USER_MODEL)),
                ('reviewer', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='ratings_given', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.AddConstraint(
            model_name='rating',
            constraint=models.UniqueConstraint(fields=('purchase_order', 'reviewer', 'reviewed'), name='unique_rating_per_trade_pair'),
        ),
        migrations.AddConstraint(
            model_name='rating',
            constraint=models.CheckConstraint(condition=models.Q(('overall_score__gte', 1), ('overall_score__lte', 5)), name='rating_score_between_1_and_5'),
        ),
        migrations.AddIndex(
            model_name='rating',
            index=models.Index(fields=['reviewed', 'created_at'], name='ratings_rat_review_57d7d0_idx'),
        ),
    ]
