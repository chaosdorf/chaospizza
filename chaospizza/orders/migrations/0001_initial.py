# Generated by Django 1.11.3 on 2017-07-07 00:59
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):  # noqa

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField()),
                ('coordinator', models.CharField(max_length=100)),
                ('restaurant_name', models.CharField(max_length=250)),
                ('state', models.CharField(choices=[('preparing', 'Order is prepared, order items can be modified.'), ('ordering', 'Order is locked and sent to delivery service by coordinator.'), ('ordered', 'Order has been sent to delivery service.'), ('delivered', 'Delivery has arrived.'), ('canceled', 'Order has been canceled due to some reason.')], default='preparing', max_length=16)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ('history__created_at',),
            },
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('participant', models.CharField(max_length=100)),
                ('description', models.CharField(max_length=250)),
                ('price', models.DecimalField(decimal_places=2, max_digits=5)),
                ('amount', models.PositiveIntegerField(default=1)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='orders.Order')),
            ],
        ),
        migrations.CreateModel(
            name='OrderStateChange',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('old_state', models.CharField(choices=[('preparing', 'Order is prepared, order items can be modified.'), ('ordering', 'Order is locked and sent to delivery service by coordinator.'), ('ordered', 'Order has been sent to delivery service.'), ('delivered', 'Delivery has arrived.'), ('canceled', 'Order has been canceled due to some reason.')], max_length=16)),
                ('new_state', models.CharField(choices=[('preparing', 'Order is prepared, order items can be modified.'), ('ordering', 'Order is locked and sent to delivery service by coordinator.'), ('ordered', 'Order has been sent to delivery service.'), ('delivered', 'Delivery has arrived.'), ('canceled', 'Order has been canceled due to some reason.')], max_length=16)),
                ('reason', models.CharField(max_length=1000, null=True)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='history', to='orders.Order')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='order',
            unique_together=set([('coordinator', 'restaurant_name')]),
        ),
    ]
