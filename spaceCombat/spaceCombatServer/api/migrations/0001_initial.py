# Generated by Django 2.0.8 on 2018-08-19 00:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nickname', models.CharField(max_length=100)),
                ('ip_address', models.CharField(max_length=11)),
                ('room_player_id', models.IntegerField()),
                ('num_wins', models.IntegerField(default=0)),
                ('hash', models.CharField(max_length=20)),
                ('ping', models.CharField(default='999ms', max_length=5)),
            ],
            options={
                'ordering': ('room_player_id',),
            },
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('room_code', models.CharField(max_length=6, unique=True)),
                ('num_games', models.IntegerField(default=0)),
                ('port_tcp', models.IntegerField()),
                ('port_udp', models.IntegerField()),
                ('owner', models.IntegerField(default=0)),
            ],
        ),
        migrations.AddField(
            model_name='player',
            name='room',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='players', to='api.Room'),
        ),
    ]
