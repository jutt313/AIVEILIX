Last login: Mon Apr  6 11:11:34 on ttys003
You have new mail.
gcloud compute ssh aiveilix-backend-test --zone=asia-northeast1-a
chaffanjutt@Affans-MacBook-Air ~ % gcloud compute ssh aiveilix-backend-test --zone=asia-northeast1-a
Welcome to Ubuntu 22.04.5 LTS (GNU/Linux 6.8.0-1048-gcp x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/pro

 System information as of Mon Apr  6 02:11:44 UTC 2026

  System load:  0.09               Processes:             117
  Usage of /:   65.8% of 28.89GB   Users logged in:       0
  Memory usage: 22%                IPv4 address for ens4: 10.146.0.2
  Swap usage:   0%

 * Strictly confined Kubernetes makes edge and IoT secure. Learn how MicroK8s
   just raised the bar for easy, resilient and secure K8s cluster deployment.

   https://ubuntu.com/engage/secure-kubernetes-at-the-edge

Expanded Security Maintenance for Applications is not enabled.

35 updates can be applied immediately.
25 of these updates are standard security updates.
To see these additional updates run: apt list --upgradable

3 additional security updates can be applied with ESM Apps.
Learn more about enabling ESM Apps service at https://ubuntu.com/esm

New release '24.04.4 LTS' available.
Run 'do-release-upgrade' to upgrade to it.


Last login: Mon Apr  6 02:11:45 2026 from 219.107.119.157
chaffanjutt@aiveilix-backend-test:~$ cd ~/AIVEILIX/backend
source .venv/bin/activate
python run.py
INFO:     Will watch for changes in these directories: ['/home/chaffanjutt/AIVEILIX/backend']
ERROR:    [Errno 98] Address already in use
(.venv) chaffanjutt@aiveilix-backend-test:~/AIVEILIX/backend$ pkill -f "python run.py"
cd ~/AIVEILIX/backend
source .venv/bin/activate
python run.py
INFO:     Will watch for changes in these directories: ['/home/chaffanjutt/AIVEILIX/backend']
ERROR:    [Errno 98] Address already in use
(.venv) chaffanjutt@aiveilix-backend-test:~/AIVEILIX/backend$ pkill -f "python run.py"
cd ~/AIVEILIX/backend
source .venv/bin/activate
python run.py
INFO:     Will watch for changes in these directories: ['/home/chaffanjutt/AIVEILIX/backend']
ERROR:    [Errno 98] Address already in use
(.venv) chaffanjutt@aiveilix-backend-test:~/AIVEILIX/backend$ ss -ltnp | grep 4565
LISTEN 0      2048         0.0.0.0:4565      0.0.0.0:*    users:(("python",pid=18407,fd=20))
(.venv) chaffanjutt@aiveilix-backend-test:~/AIVEILIX/backend$ kill -9 PID
-bash: kill: PID: arguments must be process or job IDs
(.venv) chaffanjutt@aiveilix-backend-test:~/AIVEILIX/backend$ cd ~/AIVEILIX/backend
source .venv/bin/activate
python run.py
INFO:     Will watch for changes in these directories: ['/home/chaffanjutt/AIVEILIX/backend']
ERROR:    [Errno 98] Address already in use
(.venv) chaffanjutt@aiveilix-backend-test:~/AIVEILIX/backend$ kill -9 $(ss -ltnp | awk '/:4565/ {print $NF}' | sed -E 's/.*pid=([0-9]+).*/\1/' | head -n1)
(.venv) chaffanjutt@aiveilix-backend-test:~/AIVEILIX/backend$ python run.py
INFO:     Will watch for changes in these directories: ['/home/chaffanjutt/AIVEILIX/backend']
INFO:     Uvicorn running on http://0.0.0.0:4565 (Press CTRL+C to quit)
INFO:     Started reloader process [18941] using WatchFiles
/home/chaffanjutt/AIVEILIX/backend/.venv/lib/python3.10/site-packages/google/api_core/_python_version_support.py:263: FutureWarning: You are using a Python version (3.10.12) which Google will stop supporting in new releases of google.api_core once it reaches its end of life (2026-10-04). Please upgrade to the latest Python version, or at least Python 3.11, to continue receiving updates for google.api_core past that date.
  warnings.warn(message, FutureWarning)
INFO      datasets                                  PyTorch version 2.11.0 available.
INFO:     Started server process [18943]
INFO:     Waiting for application startup.
2026-04-06 02:13:35,704 INFO sqlalchemy.engine.Engine select pg_catalog.version()
INFO      sqlalchemy.engine.Engine                  select pg_catalog.version()
2026-04-06 02:13:35,705 INFO sqlalchemy.engine.Engine [raw sql] ()
INFO      sqlalchemy.engine.Engine                  [raw sql] ()
2026-04-06 02:13:35,709 INFO sqlalchemy.engine.Engine select current_schema()
INFO      sqlalchemy.engine.Engine                  select current_schema()
2026-04-06 02:13:35,710 INFO sqlalchemy.engine.Engine [raw sql] ()
INFO      sqlalchemy.engine.Engine                  [raw sql] ()
2026-04-06 02:13:35,713 INFO sqlalchemy.engine.Engine show standard_conforming_strings
INFO      sqlalchemy.engine.Engine                  show standard_conforming_strings
2026-04-06 02:13:35,713 INFO sqlalchemy.engine.Engine [raw sql] ()
INFO      sqlalchemy.engine.Engine                  [raw sql] ()
2026-04-06 02:13:35,716 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:13:35,716 INFO sqlalchemy.engine.Engine SELECT current_database() AS db, current_user AS user_name, version() AS version
INFO      sqlalchemy.engine.Engine                  SELECT current_database() AS db, current_user AS user_name, version() AS version
2026-04-06 02:13:35,716 INFO sqlalchemy.engine.Engine [generated in 0.00086s] ()
INFO      sqlalchemy.engine.Engine                  [generated in 0.00086s] ()
2026-04-06 02:13:35,718 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
/home/chaffanjutt/AIVEILIX/backend/app/services/qdrant/file_indexer.py:111: UserWarning: Payload indexes have no effect in the local Qdrant. Please use server Qdrant if you need payload indexes.
  await client.create_payload_index(
DEBUG     app.services.qdrant.file_indexer          Payload indexes ensured for collection: text_chunks
DEBUG     app.services.qdrant.file_indexer          Payload indexes ensured for collection: image_chunks
INFO:     Application startup complete.
2026-04-06 02:13:59,768 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:13:59,858 INFO sqlalchemy.engine.Engine SELECT users.id, users.email, users.password_hash, users.provider, users.provider_id, users.is_verified, users.is_active, users.two_factor_enabled, users.two_factor_secret, users.two_factor_backup_codes, users.created_at, users.updated_at 
FROM users 
WHERE users.email = $1::VARCHAR
INFO      sqlalchemy.engine.Engine                  SELECT users.id, users.email, users.password_hash, users.provider, users.provider_id, users.is_verified, users.is_active, users.two_factor_enabled, users.two_factor_secret, users.two_factor_backup_codes, users.created_at, users.updated_at 
FROM users 
WHERE users.email = $1::VARCHAR
2026-04-06 02:13:59,859 INFO sqlalchemy.engine.Engine [generated in 0.00091s] ('chaffanjutt313@gmail.com',)
INFO      sqlalchemy.engine.Engine                  [generated in 0.00091s] ('chaffanjutt313@gmail.com',)
2026-04-06 02:14:00,372 INFO sqlalchemy.engine.Engine INSERT INTO notifications (id, user_id, type, title, message, is_read) VALUES ($1::UUID, $2::UUID, $3::notification_type, $4::VARCHAR, $5::VARCHAR, $6::BOOLEAN) RETURNING notifications.created_at
INFO      sqlalchemy.engine.Engine                  INSERT INTO notifications (id, user_id, type, title, message, is_read) VALUES ($1::UUID, $2::UUID, $3::notification_type, $4::VARCHAR, $5::VARCHAR, $6::BOOLEAN) RETURNING notifications.created_at
2026-04-06 02:14:00,373 INFO sqlalchemy.engine.Engine [generated in 0.00067s] (UUID('eead62bc-8dad-4975-9b79-de10c9a0afc1'), UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), 'info', 'Signed in', 'You signed in to your AIveilix account.', False)
INFO      sqlalchemy.engine.Engine                  [generated in 0.00067s] (UUID('eead62bc-8dad-4975-9b79-de10c9a0afc1'), UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), 'info', 'Signed in', 'You signed in to your AIveilix account.', False)
2026-04-06 02:14:00,398 INFO sqlalchemy.engine.Engine COMMIT
INFO      sqlalchemy.engine.Engine                  COMMIT
2026-04-06 02:14:00,406 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:14:00,408 INFO sqlalchemy.engine.Engine SELECT notifications.id, notifications.user_id, notifications.type, notifications.title, notifications.message, notifications.is_read, notifications.created_at 
FROM notifications 
WHERE notifications.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT notifications.id, notifications.user_id, notifications.type, notifications.title, notifications.message, notifications.is_read, notifications.created_at 
FROM notifications 
WHERE notifications.id = $1::UUID
2026-04-06 02:14:00,409 INFO sqlalchemy.engine.Engine [generated in 0.00115s] (UUID('eead62bc-8dad-4975-9b79-de10c9a0afc1'),)
INFO      sqlalchemy.engine.Engine                  [generated in 0.00115s] (UUID('eead62bc-8dad-4975-9b79-de10c9a0afc1'),)
2026-04-06 02:14:00,416 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:14:00,615 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:14:00,618 INFO sqlalchemy.engine.Engine SELECT users.id, users.email, users.password_hash, users.provider, users.provider_id, users.is_verified, users.is_active, users.two_factor_enabled, users.two_factor_secret, users.two_factor_backup_codes, users.created_at, users.updated_at 
FROM users 
WHERE users.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT users.id, users.email, users.password_hash, users.provider, users.provider_id, users.is_verified, users.is_active, users.two_factor_enabled, users.two_factor_secret, users.two_factor_backup_codes, users.created_at, users.updated_at 
FROM users 
WHERE users.id = $1::UUID
2026-04-06 02:14:00,618 INFO sqlalchemy.engine.Engine [generated in 0.00058s] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'),)
INFO      sqlalchemy.engine.Engine                  [generated in 0.00058s] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'),)
2026-04-06 02:14:00,636 INFO sqlalchemy.engine.Engine SELECT profiles.id, profiles.user_id, profiles.full_name, profiles.avatar_url, profiles.bio, profiles.theme, profiles.language, profiles.timezone, profiles.preferred_llm, profiles.follow_up_mode, profiles.use_case, profiles.referral_source, profiles.updated_at 
FROM profiles 
WHERE profiles.user_id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT profiles.id, profiles.user_id, profiles.full_name, profiles.avatar_url, profiles.bio, profiles.theme, profiles.language, profiles.timezone, profiles.preferred_llm, profiles.follow_up_mode, profiles.use_case, profiles.referral_source, profiles.updated_at 
FROM profiles 
WHERE profiles.user_id = $1::UUID
2026-04-06 02:14:00,637 INFO sqlalchemy.engine.Engine [generated in 0.00077s] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'),)
INFO      sqlalchemy.engine.Engine                  [generated in 0.00077s] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'),)
2026-04-06 02:14:00,813 INFO sqlalchemy.engine.Engine SELECT oauth_tokens.provider 
FROM oauth_tokens 
WHERE oauth_tokens.user_id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT oauth_tokens.provider 
FROM oauth_tokens 
WHERE oauth_tokens.user_id = $1::UUID
2026-04-06 02:14:00,813 INFO sqlalchemy.engine.Engine [generated in 0.00071s] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'),)
INFO      sqlalchemy.engine.Engine                  [generated in 0.00071s] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'),)
2026-04-06 02:14:00,821 INFO sqlalchemy.engine.Engine COMMIT
INFO      sqlalchemy.engine.Engine                  COMMIT
2026-04-06 02:14:00,822 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:14:00,827 INFO sqlalchemy.engine.Engine SELECT buckets.id, buckets.user_id, buckets.name, buckets.description, buckets.mcp_url, buckets.mcp_token, buckets.account_mcp_url, buckets.account_mcp_token, buckets.color, buckets.icon, buckets.is_public, buckets.storage_used, buckets.created_at, buckets.updated_at 
FROM buckets 
WHERE buckets.user_id = $1::UUID ORDER BY buckets.updated_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id, buckets.user_id, buckets.name, buckets.description, buckets.mcp_url, buckets.mcp_token, buckets.account_mcp_url, buckets.account_mcp_token, buckets.color, buckets.icon, buckets.is_public, buckets.storage_used, buckets.created_at, buckets.updated_at 
FROM buckets 
WHERE buckets.user_id = $1::UUID ORDER BY buckets.updated_at DESC
2026-04-06 02:14:00,828 INFO sqlalchemy.engine.Engine [generated in 0.00111s] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'),)
INFO      sqlalchemy.engine.Engine                  [generated in 0.00111s] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'),)
2026-04-06 02:14:00,831 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:14:00,836 INFO sqlalchemy.engine.Engine SELECT coalesce(sum(files.size), $1::INTEGER) AS coalesce_1, count(files.id) AS count_1 
FROM files JOIN buckets ON files.bucket_id = buckets.id 
WHERE buckets.user_id = $2::UUID
INFO      sqlalchemy.engine.Engine                  SELECT coalesce(sum(files.size), $1::INTEGER) AS coalesce_1, count(files.id) AS count_1 
FROM files JOIN buckets ON files.bucket_id = buckets.id 
WHERE buckets.user_id = $2::UUID
2026-04-06 02:14:00,836 INFO sqlalchemy.engine.Engine [generated in 0.00057s] (0, UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'))
INFO      sqlalchemy.engine.Engine                  [generated in 0.00057s] (0, UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'))
2026-04-06 02:14:00,838 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:14:00,839 INFO sqlalchemy.engine.Engine SELECT notifications.id, notifications.user_id, notifications.type, notifications.title, notifications.message, notifications.is_read, notifications.created_at 
FROM notifications 
WHERE notifications.user_id = $1::UUID ORDER BY notifications.created_at DESC 
 LIMIT $2::INTEGER
INFO      sqlalchemy.engine.Engine                  SELECT notifications.id, notifications.user_id, notifications.type, notifications.title, notifications.message, notifications.is_read, notifications.created_at 
FROM notifications 
WHERE notifications.user_id = $1::UUID ORDER BY notifications.created_at DESC 
 LIMIT $2::INTEGER
2026-04-06 02:14:00,840 INFO sqlalchemy.engine.Engine [generated in 0.00071s] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), 20)
INFO      sqlalchemy.engine.Engine                  [generated in 0.00071s] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), 20)
2026-04-06 02:14:00,842 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:14:00,845 INFO sqlalchemy.engine.Engine SELECT count(buckets.id) AS count_1 
FROM buckets 
WHERE buckets.user_id = $1::UUID AND buckets.created_at < $2::DATE
INFO      sqlalchemy.engine.Engine                  SELECT count(buckets.id) AS count_1 
FROM buckets 
WHERE buckets.user_id = $1::UUID AND buckets.created_at < $2::DATE
2026-04-06 02:14:00,846 INFO sqlalchemy.engine.Engine [generated in 0.00122s] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), datetime.date(2025, 11, 1))
INFO      sqlalchemy.engine.Engine                  [generated in 0.00122s] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), datetime.date(2025, 11, 1))
2026-04-06 02:14:00,857 INFO sqlalchemy.engine.Engine SELECT files.bucket_id, count(files.id) AS count_1, coalesce(sum(files.size), $1::INTEGER) AS coalesce_1 
FROM files 
WHERE files.bucket_id IN ($2::UUID, $3::UUID) GROUP BY files.bucket_id
INFO      sqlalchemy.engine.Engine                  SELECT files.bucket_id, count(files.id) AS count_1, coalesce(sum(files.size), $1::INTEGER) AS coalesce_1 
FROM files 
WHERE files.bucket_id IN ($2::UUID, $3::UUID) GROUP BY files.bucket_id
2026-04-06 02:14:00,857 INFO sqlalchemy.engine.Engine [generated in 0.00081s] (0, UUID('fe09f04f-d026-46bb-ba04-67d06a415573'), UUID('083d9deb-aab6-48e9-9e73-80c4f63676d5'))
INFO      sqlalchemy.engine.Engine                  [generated in 0.00081s] (0, UUID('fe09f04f-d026-46bb-ba04-67d06a415573'), UUID('083d9deb-aab6-48e9-9e73-80c4f63676d5'))
2026-04-06 02:14:00,862 INFO sqlalchemy.engine.Engine SELECT count(*) AS count_1 
FROM buckets 
WHERE buckets.user_id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT count(*) AS count_1 
FROM buckets 
WHERE buckets.user_id = $1::UUID
2026-04-06 02:14:00,863 INFO sqlalchemy.engine.Engine [generated in 0.00054s] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'),)
INFO      sqlalchemy.engine.Engine                  [generated in 0.00054s] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'),)
2026-04-06 02:14:00,869 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:14:00,873 INFO sqlalchemy.engine.Engine SELECT count(messages.id) AS count_1 
FROM messages JOIN conversations ON messages.conversation_id = conversations.id 
WHERE conversations.user_id = $1::UUID AND messages.created_at >= $2::DATE
INFO      sqlalchemy.engine.Engine                  SELECT count(messages.id) AS count_1 
FROM messages JOIN conversations ON messages.conversation_id = conversations.id 
WHERE conversations.user_id = $1::UUID AND messages.created_at >= $2::DATE
2026-04-06 02:14:00,873 INFO sqlalchemy.engine.Engine [generated in 0.00069s] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), datetime.date(2026, 4, 1))
INFO      sqlalchemy.engine.Engine                  [generated in 0.00069s] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), datetime.date(2026, 4, 1))
2026-04-06 02:14:00,885 INFO sqlalchemy.engine.Engine SELECT count(files.id) AS count_1, coalesce(sum(files.size), $1::INTEGER) AS coalesce_1 
FROM files JOIN buckets ON files.bucket_id = buckets.id 
WHERE buckets.user_id = $2::UUID AND files.created_at < $3::DATE
INFO      sqlalchemy.engine.Engine                  SELECT count(files.id) AS count_1, coalesce(sum(files.size), $1::INTEGER) AS coalesce_1 
FROM files JOIN buckets ON files.bucket_id = buckets.id 
WHERE buckets.user_id = $2::UUID AND files.created_at < $3::DATE
2026-04-06 02:14:00,886 INFO sqlalchemy.engine.Engine [generated in 0.00062s] (0, UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), datetime.date(2025, 11, 1))
INFO      sqlalchemy.engine.Engine                  [generated in 0.00062s] (0, UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), datetime.date(2025, 11, 1))
2026-04-06 02:14:00,898 INFO sqlalchemy.engine.Engine SELECT usage_tracking.id, usage_tracking.user_id, usage_tracking.month, usage_tracking.storage_used, usage_tracking.chat_messages_count, usage_tracking.mcp_calls_count, usage_tracking.buckets_count, usage_tracking.files_count, usage_tracking.updated_at 
FROM usage_tracking 
WHERE usage_tracking.user_id = $1::UUID AND usage_tracking.month = $2::DATE
INFO      sqlalchemy.engine.Engine                  SELECT usage_tracking.id, usage_tracking.user_id, usage_tracking.month, usage_tracking.storage_used, usage_tracking.chat_messages_count, usage_tracking.mcp_calls_count, usage_tracking.buckets_count, usage_tracking.files_count, usage_tracking.updated_at 
FROM usage_tracking 
WHERE usage_tracking.user_id = $1::UUID AND usage_tracking.month = $2::DATE
2026-04-06 02:14:00,898 INFO sqlalchemy.engine.Engine [generated in 0.00104s] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), datetime.date(2026, 4, 1))
INFO      sqlalchemy.engine.Engine                  [generated in 0.00104s] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), datetime.date(2026, 4, 1))
2026-04-06 02:14:00,899 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:14:00,900 INFO sqlalchemy.engine.Engine SELECT users.id, users.email, users.password_hash, users.provider, users.provider_id, users.is_verified, users.is_active, users.two_factor_enabled, users.two_factor_secret, users.two_factor_backup_codes, users.created_at, users.updated_at 
FROM users 
WHERE users.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT users.id, users.email, users.password_hash, users.provider, users.provider_id, users.is_verified, users.is_active, users.two_factor_enabled, users.two_factor_secret, users.two_factor_backup_codes, users.created_at, users.updated_at 
FROM users 
WHERE users.id = $1::UUID
2026-04-06 02:14:00,901 INFO sqlalchemy.engine.Engine [cached since 0.2829s ago] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'),)
INFO      sqlalchemy.engine.Engine                  [cached since 0.2829s ago] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'),)
2026-04-06 02:14:00,908 INFO sqlalchemy.engine.Engine SELECT date_trunc($1::VARCHAR, buckets.created_at) AS bucket_month, count(buckets.id) AS count_1 
FROM buckets 
WHERE buckets.user_id = $2::UUID AND buckets.created_at >= $3::DATE AND buckets.created_at < $4::DATE GROUP BY date_trunc($1::VARCHAR, buckets.created_at) ORDER BY bucket_month ASC
INFO      sqlalchemy.engine.Engine                  SELECT date_trunc($1::VARCHAR, buckets.created_at) AS bucket_month, count(buckets.id) AS count_1 
FROM buckets 
WHERE buckets.user_id = $2::UUID AND buckets.created_at >= $3::DATE AND buckets.created_at < $4::DATE GROUP BY date_trunc($1::VARCHAR, buckets.created_at) ORDER BY bucket_month ASC
2026-04-06 02:14:00,909 INFO sqlalchemy.engine.Engine [generated in 0.00116s] ('month', UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), datetime.date(2025, 11, 1), datetime.date(2026, 5, 1))
INFO      sqlalchemy.engine.Engine                  [generated in 0.00116s] ('month', UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), datetime.date(2025, 11, 1), datetime.date(2026, 5, 1))
2026-04-06 02:14:01,254 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:14:01,260 INFO sqlalchemy.engine.Engine SELECT date_trunc($1::VARCHAR, files.created_at) AS file_month, count(files.id) AS count_1, coalesce(sum(files.size), $2::INTEGER) AS coalesce_1 
FROM files JOIN buckets ON files.bucket_id = buckets.id 
WHERE buckets.user_id = $3::UUID AND files.created_at >= $4::DATE AND files.created_at < $5::DATE GROUP BY date_trunc($1::VARCHAR, files.created_at) ORDER BY file_month ASC
INFO      sqlalchemy.engine.Engine                  SELECT date_trunc($1::VARCHAR, files.created_at) AS file_month, count(files.id) AS count_1, coalesce(sum(files.size), $2::INTEGER) AS coalesce_1 
FROM files JOIN buckets ON files.bucket_id = buckets.id 
WHERE buckets.user_id = $3::UUID AND files.created_at >= $4::DATE AND files.created_at < $5::DATE GROUP BY date_trunc($1::VARCHAR, files.created_at) ORDER BY file_month ASC
2026-04-06 02:14:01,260 INFO sqlalchemy.engine.Engine [generated in 0.00059s] ('month', 0, UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), datetime.date(2025, 11, 1), datetime.date(2026, 5, 1))
INFO      sqlalchemy.engine.Engine                  [generated in 0.00059s] ('month', 0, UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), datetime.date(2025, 11, 1), datetime.date(2026, 5, 1))
2026-04-06 02:14:01,262 INFO sqlalchemy.engine.Engine SELECT profiles.id, profiles.user_id, profiles.full_name, profiles.avatar_url, profiles.bio, profiles.theme, profiles.language, profiles.timezone, profiles.preferred_llm, profiles.follow_up_mode, profiles.use_case, profiles.referral_source, profiles.updated_at 
FROM profiles 
WHERE profiles.user_id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT profiles.id, profiles.user_id, profiles.full_name, profiles.avatar_url, profiles.bio, profiles.theme, profiles.language, profiles.timezone, profiles.preferred_llm, profiles.follow_up_mode, profiles.use_case, profiles.referral_source, profiles.updated_at 
FROM profiles 
WHERE profiles.user_id = $1::UUID
2026-04-06 02:14:01,262 INFO sqlalchemy.engine.Engine [cached since 0.6262s ago] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'),)
INFO      sqlalchemy.engine.Engine                  [cached since 0.6262s ago] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'),)
2026-04-06 02:14:01,265 INFO sqlalchemy.engine.Engine SELECT oauth_tokens.provider 
FROM oauth_tokens 
WHERE oauth_tokens.user_id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT oauth_tokens.provider 
FROM oauth_tokens 
WHERE oauth_tokens.user_id = $1::UUID
2026-04-06 02:14:01,266 INFO sqlalchemy.engine.Engine [cached since 0.4535s ago] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'),)
INFO      sqlalchemy.engine.Engine                  [cached since 0.4535s ago] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'),)
2026-04-06 02:14:01,270 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:14:01,271 INFO sqlalchemy.engine.Engine COMMIT
INFO      sqlalchemy.engine.Engine                  COMMIT
2026-04-06 02:14:01,276 INFO sqlalchemy.engine.Engine SELECT date_trunc($1::VARCHAR, messages.created_at) AS message_month, count(messages.id) AS count_1 
FROM messages JOIN conversations ON messages.conversation_id = conversations.id 
WHERE conversations.user_id = $2::UUID AND messages.created_at >= $3::DATE AND messages.created_at < $4::DATE GROUP BY date_trunc($1::VARCHAR, messages.created_at) ORDER BY message_month ASC
INFO      sqlalchemy.engine.Engine                  SELECT date_trunc($1::VARCHAR, messages.created_at) AS message_month, count(messages.id) AS count_1 
FROM messages JOIN conversations ON messages.conversation_id = conversations.id 
WHERE conversations.user_id = $2::UUID AND messages.created_at >= $3::DATE AND messages.created_at < $4::DATE GROUP BY date_trunc($1::VARCHAR, messages.created_at) ORDER BY message_month ASC
2026-04-06 02:14:01,276 INFO sqlalchemy.engine.Engine [generated in 0.00068s] ('month', UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), datetime.date(2025, 11, 1), datetime.date(2026, 5, 1))
INFO      sqlalchemy.engine.Engine                  [generated in 0.00068s] ('month', UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), datetime.date(2025, 11, 1), datetime.date(2026, 5, 1))
2026-04-06 02:14:01,281 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:14:01,282 INFO sqlalchemy.engine.Engine SELECT buckets.id, buckets.user_id, buckets.name, buckets.description, buckets.mcp_url, buckets.mcp_token, buckets.account_mcp_url, buckets.account_mcp_token, buckets.color, buckets.icon, buckets.is_public, buckets.storage_used, buckets.created_at, buckets.updated_at 
FROM buckets 
WHERE buckets.user_id = $1::UUID ORDER BY buckets.updated_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id, buckets.user_id, buckets.name, buckets.description, buckets.mcp_url, buckets.mcp_token, buckets.account_mcp_url, buckets.account_mcp_token, buckets.color, buckets.icon, buckets.is_public, buckets.storage_used, buckets.created_at, buckets.updated_at 
FROM buckets 
WHERE buckets.user_id = $1::UUID ORDER BY buckets.updated_at DESC
2026-04-06 02:14:01,282 INFO sqlalchemy.engine.Engine [cached since 0.4554s ago] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'),)
INFO      sqlalchemy.engine.Engine                  [cached since 0.4554s ago] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'),)
2026-04-06 02:14:01,286 INFO sqlalchemy.engine.Engine SELECT usage_tracking.month, usage_tracking.mcp_calls_count 
FROM usage_tracking 
WHERE usage_tracking.user_id = $1::UUID AND usage_tracking.month >= $2::DATE AND usage_tracking.month <= $3::DATE ORDER BY usage_tracking.month ASC
INFO      sqlalchemy.engine.Engine                  SELECT usage_tracking.month, usage_tracking.mcp_calls_count 
FROM usage_tracking 
WHERE usage_tracking.user_id = $1::UUID AND usage_tracking.month >= $2::DATE AND usage_tracking.month <= $3::DATE ORDER BY usage_tracking.month ASC
2026-04-06 02:14:01,287 INFO sqlalchemy.engine.Engine [generated in 0.00063s] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), datetime.date(2025, 11, 1), datetime.date(2026, 4, 1))
INFO      sqlalchemy.engine.Engine                  [generated in 0.00063s] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), datetime.date(2025, 11, 1), datetime.date(2026, 4, 1))
2026-04-06 02:14:01,291 INFO sqlalchemy.engine.Engine SELECT files.bucket_id, count(files.id) AS count_1, coalesce(sum(files.size), $1::INTEGER) AS coalesce_1 
FROM files 
WHERE files.bucket_id IN ($2::UUID, $3::UUID) GROUP BY files.bucket_id
INFO      sqlalchemy.engine.Engine                  SELECT files.bucket_id, count(files.id) AS count_1, coalesce(sum(files.size), $1::INTEGER) AS coalesce_1 
FROM files 
WHERE files.bucket_id IN ($2::UUID, $3::UUID) GROUP BY files.bucket_id
2026-04-06 02:14:01,292 INFO sqlalchemy.engine.Engine [cached since 0.4355s ago] (0, UUID('fe09f04f-d026-46bb-ba04-67d06a415573'), UUID('083d9deb-aab6-48e9-9e73-80c4f63676d5'))
INFO      sqlalchemy.engine.Engine                  [cached since 0.4355s ago] (0, UUID('fe09f04f-d026-46bb-ba04-67d06a415573'), UUID('083d9deb-aab6-48e9-9e73-80c4f63676d5'))
2026-04-06 02:14:01,297 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:14:01,298 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:14:01,301 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:14:01,302 INFO sqlalchemy.engine.Engine SELECT coalesce(sum(files.size), $1::INTEGER) AS coalesce_1, count(files.id) AS count_1 
FROM files JOIN buckets ON files.bucket_id = buckets.id 
WHERE buckets.user_id = $2::UUID
INFO      sqlalchemy.engine.Engine                  SELECT coalesce(sum(files.size), $1::INTEGER) AS coalesce_1, count(files.id) AS count_1 
FROM files JOIN buckets ON files.bucket_id = buckets.id 
WHERE buckets.user_id = $2::UUID
2026-04-06 02:14:01,302 INFO sqlalchemy.engine.Engine [cached since 0.4664s ago] (0, UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'))
INFO      sqlalchemy.engine.Engine                  [cached since 0.4664s ago] (0, UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'))
2026-04-06 02:14:01,306 INFO sqlalchemy.engine.Engine SELECT count(*) AS count_1 
FROM buckets 
WHERE buckets.user_id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT count(*) AS count_1 
FROM buckets 
WHERE buckets.user_id = $1::UUID
2026-04-06 02:14:01,306 INFO sqlalchemy.engine.Engine [cached since 0.444s ago] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'),)
INFO      sqlalchemy.engine.Engine                  [cached since 0.444s ago] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'),)
2026-04-06 02:14:01,309 INFO sqlalchemy.engine.Engine SELECT count(messages.id) AS count_1 
FROM messages JOIN conversations ON messages.conversation_id = conversations.id 
WHERE conversations.user_id = $1::UUID AND messages.created_at >= $2::DATE
INFO      sqlalchemy.engine.Engine                  SELECT count(messages.id) AS count_1 
FROM messages JOIN conversations ON messages.conversation_id = conversations.id 
WHERE conversations.user_id = $1::UUID AND messages.created_at >= $2::DATE
2026-04-06 02:14:01,309 INFO sqlalchemy.engine.Engine [cached since 0.4366s ago] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), datetime.date(2026, 4, 1))
INFO      sqlalchemy.engine.Engine                  [cached since 0.4366s ago] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), datetime.date(2026, 4, 1))
2026-04-06 02:14:01,311 INFO sqlalchemy.engine.Engine SELECT usage_tracking.id, usage_tracking.user_id, usage_tracking.month, usage_tracking.storage_used, usage_tracking.chat_messages_count, usage_tracking.mcp_calls_count, usage_tracking.buckets_count, usage_tracking.files_count, usage_tracking.updated_at 
FROM usage_tracking 
WHERE usage_tracking.user_id = $1::UUID AND usage_tracking.month = $2::DATE
INFO      sqlalchemy.engine.Engine                  SELECT usage_tracking.id, usage_tracking.user_id, usage_tracking.month, usage_tracking.storage_used, usage_tracking.chat_messages_count, usage_tracking.mcp_calls_count, usage_tracking.buckets_count, usage_tracking.files_count, usage_tracking.updated_at 
FROM usage_tracking 
WHERE usage_tracking.user_id = $1::UUID AND usage_tracking.month = $2::DATE
2026-04-06 02:14:01,312 INFO sqlalchemy.engine.Engine [cached since 0.4145s ago] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), datetime.date(2026, 4, 1))
INFO      sqlalchemy.engine.Engine                  [cached since 0.4145s ago] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), datetime.date(2026, 4, 1))
2026-04-06 02:14:01,313 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:14:01,313 INFO sqlalchemy.engine.Engine SELECT notifications.id, notifications.user_id, notifications.type, notifications.title, notifications.message, notifications.is_read, notifications.created_at 
FROM notifications 
WHERE notifications.user_id = $1::UUID ORDER BY notifications.created_at DESC 
 LIMIT $2::INTEGER
INFO      sqlalchemy.engine.Engine                  SELECT notifications.id, notifications.user_id, notifications.type, notifications.title, notifications.message, notifications.is_read, notifications.created_at 
FROM notifications 
WHERE notifications.user_id = $1::UUID ORDER BY notifications.created_at DESC 
 LIMIT $2::INTEGER
2026-04-06 02:14:01,313 INFO sqlalchemy.engine.Engine [cached since 0.4742s ago] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), 20)
INFO      sqlalchemy.engine.Engine                  [cached since 0.4742s ago] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), 20)
2026-04-06 02:14:01,315 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:14:01,318 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:14:01,325 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:14:01,326 INFO sqlalchemy.engine.Engine SELECT count(buckets.id) AS count_1 
FROM buckets 
WHERE buckets.user_id = $1::UUID AND buckets.created_at < $2::DATE
INFO      sqlalchemy.engine.Engine                  SELECT count(buckets.id) AS count_1 
FROM buckets 
WHERE buckets.user_id = $1::UUID AND buckets.created_at < $2::DATE
2026-04-06 02:14:01,326 INFO sqlalchemy.engine.Engine [cached since 0.4812s ago] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), datetime.date(2025, 11, 1))
INFO      sqlalchemy.engine.Engine                  [cached since 0.4812s ago] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), datetime.date(2025, 11, 1))
2026-04-06 02:14:01,332 INFO sqlalchemy.engine.Engine SELECT count(files.id) AS count_1, coalesce(sum(files.size), $1::INTEGER) AS coalesce_1 
FROM files JOIN buckets ON files.bucket_id = buckets.id 
WHERE buckets.user_id = $2::UUID AND files.created_at < $3::DATE
INFO      sqlalchemy.engine.Engine                  SELECT count(files.id) AS count_1, coalesce(sum(files.size), $1::INTEGER) AS coalesce_1 
FROM files JOIN buckets ON files.bucket_id = buckets.id 
WHERE buckets.user_id = $2::UUID AND files.created_at < $3::DATE
2026-04-06 02:14:01,332 INFO sqlalchemy.engine.Engine [cached since 0.4473s ago] (0, UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), datetime.date(2025, 11, 1))
INFO      sqlalchemy.engine.Engine                  [cached since 0.4473s ago] (0, UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), datetime.date(2025, 11, 1))
2026-04-06 02:14:01,338 INFO sqlalchemy.engine.Engine SELECT date_trunc($1::VARCHAR, buckets.created_at) AS bucket_month, count(buckets.id) AS count_1 
FROM buckets 
WHERE buckets.user_id = $2::UUID AND buckets.created_at >= $3::DATE AND buckets.created_at < $4::DATE GROUP BY date_trunc($1::VARCHAR, buckets.created_at) ORDER BY bucket_month ASC
INFO      sqlalchemy.engine.Engine                  SELECT date_trunc($1::VARCHAR, buckets.created_at) AS bucket_month, count(buckets.id) AS count_1 
FROM buckets 
WHERE buckets.user_id = $2::UUID AND buckets.created_at >= $3::DATE AND buckets.created_at < $4::DATE GROUP BY date_trunc($1::VARCHAR, buckets.created_at) ORDER BY bucket_month ASC
2026-04-06 02:14:01,339 INFO sqlalchemy.engine.Engine [cached since 0.4307s ago] ('month', UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), datetime.date(2025, 11, 1), datetime.date(2026, 5, 1))
INFO      sqlalchemy.engine.Engine                  [cached since 0.4307s ago] ('month', UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), datetime.date(2025, 11, 1), datetime.date(2026, 5, 1))
2026-04-06 02:14:01,344 INFO sqlalchemy.engine.Engine SELECT date_trunc($1::VARCHAR, files.created_at) AS file_month, count(files.id) AS count_1, coalesce(sum(files.size), $2::INTEGER) AS coalesce_1 
FROM files JOIN buckets ON files.bucket_id = buckets.id 
WHERE buckets.user_id = $3::UUID AND files.created_at >= $4::DATE AND files.created_at < $5::DATE GROUP BY date_trunc($1::VARCHAR, files.created_at) ORDER BY file_month ASC
INFO      sqlalchemy.engine.Engine                  SELECT date_trunc($1::VARCHAR, files.created_at) AS file_month, count(files.id) AS count_1, coalesce(sum(files.size), $2::INTEGER) AS coalesce_1 
FROM files JOIN buckets ON files.bucket_id = buckets.id 
WHERE buckets.user_id = $3::UUID AND files.created_at >= $4::DATE AND files.created_at < $5::DATE GROUP BY date_trunc($1::VARCHAR, files.created_at) ORDER BY file_month ASC
2026-04-06 02:14:01,345 INFO sqlalchemy.engine.Engine [cached since 0.08484s ago] ('month', 0, UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), datetime.date(2025, 11, 1), datetime.date(2026, 5, 1))
INFO      sqlalchemy.engine.Engine                  [cached since 0.08484s ago] ('month', 0, UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), datetime.date(2025, 11, 1), datetime.date(2026, 5, 1))
2026-04-06 02:14:01,348 INFO sqlalchemy.engine.Engine SELECT date_trunc($1::VARCHAR, messages.created_at) AS message_month, count(messages.id) AS count_1 
FROM messages JOIN conversations ON messages.conversation_id = conversations.id 
WHERE conversations.user_id = $2::UUID AND messages.created_at >= $3::DATE AND messages.created_at < $4::DATE GROUP BY date_trunc($1::VARCHAR, messages.created_at) ORDER BY message_month ASC
INFO      sqlalchemy.engine.Engine                  SELECT date_trunc($1::VARCHAR, messages.created_at) AS message_month, count(messages.id) AS count_1 
FROM messages JOIN conversations ON messages.conversation_id = conversations.id 
WHERE conversations.user_id = $2::UUID AND messages.created_at >= $3::DATE AND messages.created_at < $4::DATE GROUP BY date_trunc($1::VARCHAR, messages.created_at) ORDER BY message_month ASC
2026-04-06 02:14:01,349 INFO sqlalchemy.engine.Engine [cached since 0.0732s ago] ('month', UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), datetime.date(2025, 11, 1), datetime.date(2026, 5, 1))
INFO      sqlalchemy.engine.Engine                  [cached since 0.0732s ago] ('month', UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), datetime.date(2025, 11, 1), datetime.date(2026, 5, 1))
2026-04-06 02:14:01,353 INFO sqlalchemy.engine.Engine SELECT usage_tracking.month, usage_tracking.mcp_calls_count 
FROM usage_tracking 
WHERE usage_tracking.user_id = $1::UUID AND usage_tracking.month >= $2::DATE AND usage_tracking.month <= $3::DATE ORDER BY usage_tracking.month ASC
INFO      sqlalchemy.engine.Engine                  SELECT usage_tracking.month, usage_tracking.mcp_calls_count 
FROM usage_tracking 
WHERE usage_tracking.user_id = $1::UUID AND usage_tracking.month >= $2::DATE AND usage_tracking.month <= $3::DATE ORDER BY usage_tracking.month ASC
2026-04-06 02:14:01,354 INFO sqlalchemy.engine.Engine [cached since 0.06741s ago] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), datetime.date(2025, 11, 1), datetime.date(2026, 4, 1))
INFO      sqlalchemy.engine.Engine                  [cached since 0.06741s ago] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), datetime.date(2025, 11, 1), datetime.date(2026, 4, 1))
2026-04-06 02:14:01,359 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:14:09,331 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:14:09,333 INFO sqlalchemy.engine.Engine INSERT INTO buckets (id, user_id, name, description, mcp_url, mcp_token, account_mcp_url, account_mcp_token, color, icon, is_public, storage_used) VALUES ($1::UUID, $2::UUID, $3::VARCHAR, $4::VARCHAR, $5::VARCHAR, $6::VARCHAR, $7::VARCHAR, $8::VARCHAR, $9::VARCHAR, $10::VARCHAR, $11::BOOLEAN, $12::BIGINT) RETURNING buckets.created_at, buckets.updated_at
INFO      sqlalchemy.engine.Engine                  INSERT INTO buckets (id, user_id, name, description, mcp_url, mcp_token, account_mcp_url, account_mcp_token, color, icon, is_public, storage_used) VALUES ($1::UUID, $2::UUID, $3::VARCHAR, $4::VARCHAR, $5::VARCHAR, $6::VARCHAR, $7::VARCHAR, $8::VARCHAR, $9::VARCHAR, $10::VARCHAR, $11::BOOLEAN, $12::BIGINT) RETURNING buckets.created_at, buckets.updated_at
2026-04-06 02:14:09,334 INFO sqlalchemy.engine.Engine [generated in 0.00060s] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'), UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), 'its for ', None, None, 'Sz2VTSXpFk1C9QkKWVExnR1qtchQbodc2aWzVAx1kyE', None, None, '#3B82F6', 'folder', False, 0)
INFO      sqlalchemy.engine.Engine                  [generated in 0.00060s] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'), UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), 'its for ', None, None, 'Sz2VTSXpFk1C9QkKWVExnR1qtchQbodc2aWzVAx1kyE', None, None, '#3B82F6', 'folder', False, 0)
2026-04-06 02:14:09,338 INFO sqlalchemy.engine.Engine INSERT INTO notifications (id, user_id, type, title, message, is_read) VALUES ($1::UUID, $2::UUID, $3::notification_type, $4::VARCHAR, $5::VARCHAR, $6::BOOLEAN) RETURNING notifications.created_at
INFO      sqlalchemy.engine.Engine                  INSERT INTO notifications (id, user_id, type, title, message, is_read) VALUES ($1::UUID, $2::UUID, $3::notification_type, $4::VARCHAR, $5::VARCHAR, $6::BOOLEAN) RETURNING notifications.created_at
2026-04-06 02:14:09,338 INFO sqlalchemy.engine.Engine [cached since 8.966s ago] (UUID('36b4d5e5-3cde-4c58-877a-855a726ddf7e'), UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), 'success', 'Bucket created', 'Bucket "its for " was created successfully.', False)
INFO      sqlalchemy.engine.Engine                  [cached since 8.966s ago] (UUID('36b4d5e5-3cde-4c58-877a-855a726ddf7e'), UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), 'success', 'Bucket created', 'Bucket "its for " was created successfully.', False)
2026-04-06 02:14:09,360 INFO sqlalchemy.engine.Engine COMMIT
INFO      sqlalchemy.engine.Engine                  COMMIT
2026-04-06 02:14:09,365 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:14:09,367 INFO sqlalchemy.engine.Engine SELECT buckets.id, buckets.user_id, buckets.name, buckets.description, buckets.mcp_url, buckets.mcp_token, buckets.account_mcp_url, buckets.account_mcp_token, buckets.color, buckets.icon, buckets.is_public, buckets.storage_used, buckets.created_at, buckets.updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id, buckets.user_id, buckets.name, buckets.description, buckets.mcp_url, buckets.mcp_token, buckets.account_mcp_url, buckets.account_mcp_token, buckets.color, buckets.icon, buckets.is_public, buckets.storage_used, buckets.created_at, buckets.updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:14:09,367 INFO sqlalchemy.engine.Engine [generated in 0.00048s] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [generated in 0.00048s] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:14:09,371 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:14:11,179 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:14:11,181 INFO sqlalchemy.engine.Engine SELECT buckets.id, buckets.user_id, buckets.name, buckets.description, buckets.mcp_url, buckets.mcp_token, buckets.account_mcp_url, buckets.account_mcp_token, buckets.color, buckets.icon, buckets.is_public, buckets.storage_used, buckets.created_at, buckets.updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID AND buckets.user_id = $2::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id, buckets.user_id, buckets.name, buckets.description, buckets.mcp_url, buckets.mcp_token, buckets.account_mcp_url, buckets.account_mcp_token, buckets.color, buckets.icon, buckets.is_public, buckets.storage_used, buckets.created_at, buckets.updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID AND buckets.user_id = $2::UUID
2026-04-06 02:14:11,182 INFO sqlalchemy.engine.Engine [generated in 0.00071s] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'), UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'))
INFO      sqlalchemy.engine.Engine                  [generated in 0.00071s] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'), UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'))
2026-04-06 02:14:11,189 INFO sqlalchemy.engine.Engine SELECT conversations.id, conversations.user_id, conversations.bucket_id, conversations.title, conversations.web_search_mode, conversations.follow_up_mode, conversations.is_pinned, conversations.created_at, conversations.updated_at 
FROM conversations 
WHERE conversations.user_id = $1::UUID AND conversations.bucket_id = $2::UUID ORDER BY conversations.updated_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT conversations.id, conversations.user_id, conversations.bucket_id, conversations.title, conversations.web_search_mode, conversations.follow_up_mode, conversations.is_pinned, conversations.created_at, conversations.updated_at 
FROM conversations 
WHERE conversations.user_id = $1::UUID AND conversations.bucket_id = $2::UUID ORDER BY conversations.updated_at DESC
2026-04-06 02:14:11,190 INFO sqlalchemy.engine.Engine [generated in 0.00073s] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'))
INFO      sqlalchemy.engine.Engine                  [generated in 0.00073s] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'))
2026-04-06 02:14:11,200 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:14:11,203 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:14:11,204 INFO sqlalchemy.engine.Engine [generated in 0.00078s] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [generated in 0.00078s] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:14:11,205 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:14:11,206 INFO sqlalchemy.engine.Engine SELECT buckets.id, buckets.user_id, buckets.name, buckets.description, buckets.mcp_url, buckets.mcp_token, buckets.account_mcp_url, buckets.account_mcp_token, buckets.color, buckets.icon, buckets.is_public, buckets.storage_used, buckets.created_at, buckets.updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID AND buckets.user_id = $2::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id, buckets.user_id, buckets.name, buckets.description, buckets.mcp_url, buckets.mcp_token, buckets.account_mcp_url, buckets.account_mcp_token, buckets.color, buckets.icon, buckets.is_public, buckets.storage_used, buckets.created_at, buckets.updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID AND buckets.user_id = $2::UUID
2026-04-06 02:14:11,206 INFO sqlalchemy.engine.Engine [cached since 0.02528s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'), UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'))
INFO      sqlalchemy.engine.Engine                  [cached since 0.02528s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'), UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'))
2026-04-06 02:14:11,216 INFO sqlalchemy.engine.Engine SELECT files.bucket_id, count(files.id) AS count_1, coalesce(sum(files.size), $1::INTEGER) AS coalesce_1 
FROM files 
WHERE files.bucket_id IN ($2::UUID) GROUP BY files.bucket_id
INFO      sqlalchemy.engine.Engine                  SELECT files.bucket_id, count(files.id) AS count_1, coalesce(sum(files.size), $1::INTEGER) AS coalesce_1 
FROM files 
WHERE files.bucket_id IN ($2::UUID) GROUP BY files.bucket_id
2026-04-06 02:14:11,217 INFO sqlalchemy.engine.Engine [cached since 10.36s ago] (0, UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'))
INFO      sqlalchemy.engine.Engine                  [cached since 10.36s ago] (0, UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'))
2026-04-06 02:14:11,226 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
2026-04-06 02:14:11,227 INFO sqlalchemy.engine.Engine [generated in 0.00089s] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [generated in 0.00089s] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:14:11,231 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:14:11,235 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:14:11,244 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:14:11,257 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:14:11,259 INFO sqlalchemy.engine.Engine SELECT buckets.id, buckets.user_id, buckets.name, buckets.description, buckets.mcp_url, buckets.mcp_token, buckets.account_mcp_url, buckets.account_mcp_token, buckets.color, buckets.icon, buckets.is_public, buckets.storage_used, buckets.created_at, buckets.updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID AND buckets.user_id = $2::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id, buckets.user_id, buckets.name, buckets.description, buckets.mcp_url, buckets.mcp_token, buckets.account_mcp_url, buckets.account_mcp_token, buckets.color, buckets.icon, buckets.is_public, buckets.storage_used, buckets.created_at, buckets.updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID AND buckets.user_id = $2::UUID
2026-04-06 02:14:11,259 INFO sqlalchemy.engine.Engine [cached since 0.07799s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'), UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'))
INFO      sqlalchemy.engine.Engine                  [cached since 0.07799s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'), UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'))
2026-04-06 02:14:11,269 INFO sqlalchemy.engine.Engine SELECT files.bucket_id, count(files.id) AS count_1, coalesce(sum(files.size), $1::INTEGER) AS coalesce_1 
FROM files 
WHERE files.bucket_id IN ($2::UUID) GROUP BY files.bucket_id
INFO      sqlalchemy.engine.Engine                  SELECT files.bucket_id, count(files.id) AS count_1, coalesce(sum(files.size), $1::INTEGER) AS coalesce_1 
FROM files 
WHERE files.bucket_id IN ($2::UUID) GROUP BY files.bucket_id
2026-04-06 02:14:11,270 INFO sqlalchemy.engine.Engine [cached since 10.41s ago] (0, UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'))
INFO      sqlalchemy.engine.Engine                  [cached since 10.41s ago] (0, UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'))
2026-04-06 02:14:11,272 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:14:11,272 INFO sqlalchemy.engine.Engine SELECT buckets.id, buckets.user_id, buckets.name, buckets.description, buckets.mcp_url, buckets.mcp_token, buckets.account_mcp_url, buckets.account_mcp_token, buckets.color, buckets.icon, buckets.is_public, buckets.storage_used, buckets.created_at, buckets.updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID AND buckets.user_id = $2::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id, buckets.user_id, buckets.name, buckets.description, buckets.mcp_url, buckets.mcp_token, buckets.account_mcp_url, buckets.account_mcp_token, buckets.color, buckets.icon, buckets.is_public, buckets.storage_used, buckets.created_at, buckets.updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID AND buckets.user_id = $2::UUID
2026-04-06 02:14:11,273 INFO sqlalchemy.engine.Engine [cached since 0.09162s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'), UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'))
INFO      sqlalchemy.engine.Engine                  [cached since 0.09162s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'), UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'))
2026-04-06 02:14:11,275 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:14:11,278 INFO sqlalchemy.engine.Engine SELECT conversations.id, conversations.user_id, conversations.bucket_id, conversations.title, conversations.web_search_mode, conversations.follow_up_mode, conversations.is_pinned, conversations.created_at, conversations.updated_at 
FROM conversations 
WHERE conversations.user_id = $1::UUID AND conversations.bucket_id = $2::UUID ORDER BY conversations.updated_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT conversations.id, conversations.user_id, conversations.bucket_id, conversations.title, conversations.web_search_mode, conversations.follow_up_mode, conversations.is_pinned, conversations.created_at, conversations.updated_at 
FROM conversations 
WHERE conversations.user_id = $1::UUID AND conversations.bucket_id = $2::UUID ORDER BY conversations.updated_at DESC
2026-04-06 02:14:11,279 INFO sqlalchemy.engine.Engine [cached since 0.08977s ago] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'))
INFO      sqlalchemy.engine.Engine                  [cached since 0.08977s ago] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'))
2026-04-06 02:14:11,280 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:14:11,280 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:14:11,281 INFO sqlalchemy.engine.Engine [cached since 0.0775s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 0.0775s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:14:11,286 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
2026-04-06 02:14:11,286 INFO sqlalchemy.engine.Engine [cached since 0.06032s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 0.06032s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:14:11,303 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:14:11,315 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:14:11,316 INFO sqlalchemy.engine.Engine SELECT buckets.id, buckets.user_id, buckets.name, buckets.description, buckets.mcp_url, buckets.mcp_token, buckets.account_mcp_url, buckets.account_mcp_token, buckets.color, buckets.icon, buckets.is_public, buckets.storage_used, buckets.created_at, buckets.updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID AND buckets.user_id = $2::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id, buckets.user_id, buckets.name, buckets.description, buckets.mcp_url, buckets.mcp_token, buckets.account_mcp_url, buckets.account_mcp_token, buckets.color, buckets.icon, buckets.is_public, buckets.storage_used, buckets.created_at, buckets.updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID AND buckets.user_id = $2::UUID
2026-04-06 02:14:11,316 INFO sqlalchemy.engine.Engine [cached since 0.135s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'), UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'))
INFO      sqlalchemy.engine.Engine                  [cached since 0.135s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'), UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'))
2026-04-06 02:14:11,318 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:14:11,320 INFO sqlalchemy.engine.Engine SELECT profiles.id, profiles.user_id, profiles.full_name, profiles.avatar_url, profiles.bio, profiles.theme, profiles.language, profiles.timezone, profiles.preferred_llm, profiles.follow_up_mode, profiles.use_case, profiles.referral_source, profiles.updated_at 
FROM profiles 
WHERE profiles.user_id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT profiles.id, profiles.user_id, profiles.full_name, profiles.avatar_url, profiles.bio, profiles.theme, profiles.language, profiles.timezone, profiles.preferred_llm, profiles.follow_up_mode, profiles.use_case, profiles.referral_source, profiles.updated_at 
FROM profiles 
WHERE profiles.user_id = $1::UUID
2026-04-06 02:14:11,320 INFO sqlalchemy.engine.Engine [cached since 10.68s ago] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'),)
INFO      sqlalchemy.engine.Engine                  [cached since 10.68s ago] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'),)
2026-04-06 02:14:11,333 INFO sqlalchemy.engine.Engine INSERT INTO conversations (id, user_id, bucket_id, title, web_search_mode, follow_up_mode, is_pinned) VALUES ($1::UUID, $2::UUID, $3::UUID, $4::VARCHAR, $5::web_search_mode, $6::follow_up_mode, $7::BOOLEAN) RETURNING conversations.created_at, conversations.updated_at
INFO      sqlalchemy.engine.Engine                  INSERT INTO conversations (id, user_id, bucket_id, title, web_search_mode, follow_up_mode, is_pinned) VALUES ($1::UUID, $2::UUID, $3::UUID, $4::VARCHAR, $5::web_search_mode, $6::follow_up_mode, $7::BOOLEAN) RETURNING conversations.created_at, conversations.updated_at
2026-04-06 02:14:11,334 INFO sqlalchemy.engine.Engine [generated in 0.00092s] (UUID('64984f1b-3917-46f0-9555-e0ef067c040b'), UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'), 'New Chat', 'smart', 'all_at_once', False)
INFO      sqlalchemy.engine.Engine                  [generated in 0.00092s] (UUID('64984f1b-3917-46f0-9555-e0ef067c040b'), UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'), 'New Chat', 'smart', 'all_at_once', False)
2026-04-06 02:14:11,344 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:14:11,345 INFO sqlalchemy.engine.Engine SELECT buckets.id, buckets.user_id, buckets.name, buckets.description, buckets.mcp_url, buckets.mcp_token, buckets.account_mcp_url, buckets.account_mcp_token, buckets.color, buckets.icon, buckets.is_public, buckets.storage_used, buckets.created_at, buckets.updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID AND buckets.user_id = $2::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id, buckets.user_id, buckets.name, buckets.description, buckets.mcp_url, buckets.mcp_token, buckets.account_mcp_url, buckets.account_mcp_token, buckets.color, buckets.icon, buckets.is_public, buckets.storage_used, buckets.created_at, buckets.updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID AND buckets.user_id = $2::UUID
2026-04-06 02:14:11,345 INFO sqlalchemy.engine.Engine [cached since 0.164s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'), UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'))
INFO      sqlalchemy.engine.Engine                  [cached since 0.164s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'), UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'))
2026-04-06 02:14:11,349 INFO sqlalchemy.engine.Engine SELECT profiles.id, profiles.user_id, profiles.full_name, profiles.avatar_url, profiles.bio, profiles.theme, profiles.language, profiles.timezone, profiles.preferred_llm, profiles.follow_up_mode, profiles.use_case, profiles.referral_source, profiles.updated_at 
FROM profiles 
WHERE profiles.user_id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT profiles.id, profiles.user_id, profiles.full_name, profiles.avatar_url, profiles.bio, profiles.theme, profiles.language, profiles.timezone, profiles.preferred_llm, profiles.follow_up_mode, profiles.use_case, profiles.referral_source, profiles.updated_at 
FROM profiles 
WHERE profiles.user_id = $1::UUID
2026-04-06 02:14:11,349 INFO sqlalchemy.engine.Engine [cached since 10.71s ago] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'),)
INFO      sqlalchemy.engine.Engine                  [cached since 10.71s ago] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'),)
2026-04-06 02:14:11,359 INFO sqlalchemy.engine.Engine INSERT INTO conversations (id, user_id, bucket_id, title, web_search_mode, follow_up_mode, is_pinned) VALUES ($1::UUID, $2::UUID, $3::UUID, $4::VARCHAR, $5::web_search_mode, $6::follow_up_mode, $7::BOOLEAN) RETURNING conversations.created_at, conversations.updated_at
INFO      sqlalchemy.engine.Engine                  INSERT INTO conversations (id, user_id, bucket_id, title, web_search_mode, follow_up_mode, is_pinned) VALUES ($1::UUID, $2::UUID, $3::UUID, $4::VARCHAR, $5::web_search_mode, $6::follow_up_mode, $7::BOOLEAN) RETURNING conversations.created_at, conversations.updated_at
2026-04-06 02:14:11,359 INFO sqlalchemy.engine.Engine [cached since 0.02679s ago] (UUID('5bcce52f-2acd-44fe-b6f6-6a9ae7b6fb50'), UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'), 'New Chat', 'smart', 'all_at_once', False)
INFO      sqlalchemy.engine.Engine                  [cached since 0.02679s ago] (UUID('5bcce52f-2acd-44fe-b6f6-6a9ae7b6fb50'), UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'), 'New Chat', 'smart', 'all_at_once', False)
2026-04-06 02:14:11,408 INFO sqlalchemy.engine.Engine INSERT INTO notifications (id, user_id, type, title, message, is_read) VALUES ($1::UUID, $2::UUID, $3::notification_type, $4::VARCHAR, $5::VARCHAR, $6::BOOLEAN) RETURNING notifications.created_at
INFO      sqlalchemy.engine.Engine                  INSERT INTO notifications (id, user_id, type, title, message, is_read) VALUES ($1::UUID, $2::UUID, $3::notification_type, $4::VARCHAR, $5::VARCHAR, $6::BOOLEAN) RETURNING notifications.created_at
2026-04-06 02:14:11,408 INFO sqlalchemy.engine.Engine [cached since 11.04s ago] (UUID('a3f9ebe4-ac3c-4590-8c87-105034a0951b'), UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), 'success', 'Conversation created', 'Conversation "New Chat" was created in this bucket.', False)
INFO      sqlalchemy.engine.Engine                  [cached since 11.04s ago] (UUID('a3f9ebe4-ac3c-4590-8c87-105034a0951b'), UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), 'success', 'Conversation created', 'Conversation "New Chat" was created in this bucket.', False)
2026-04-06 02:14:11,410 INFO sqlalchemy.engine.Engine INSERT INTO notifications (id, user_id, type, title, message, is_read) VALUES ($1::UUID, $2::UUID, $3::notification_type, $4::VARCHAR, $5::VARCHAR, $6::BOOLEAN) RETURNING notifications.created_at
INFO      sqlalchemy.engine.Engine                  INSERT INTO notifications (id, user_id, type, title, message, is_read) VALUES ($1::UUID, $2::UUID, $3::notification_type, $4::VARCHAR, $5::VARCHAR, $6::BOOLEAN) RETURNING notifications.created_at
2026-04-06 02:14:11,410 INFO sqlalchemy.engine.Engine [cached since 11.04s ago] (UUID('8dfbe59a-03d5-4065-b59f-d903ceab6674'), UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), 'success', 'Conversation created', 'Conversation "New Chat" was created in this bucket.', False)
INFO      sqlalchemy.engine.Engine                  [cached since 11.04s ago] (UUID('8dfbe59a-03d5-4065-b59f-d903ceab6674'), UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), 'success', 'Conversation created', 'Conversation "New Chat" was created in this bucket.', False)
2026-04-06 02:14:11,414 INFO sqlalchemy.engine.Engine COMMIT
INFO      sqlalchemy.engine.Engine                  COMMIT
2026-04-06 02:14:11,419 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:14:11,421 INFO sqlalchemy.engine.Engine SELECT conversations.id, conversations.user_id, conversations.bucket_id, conversations.title, conversations.web_search_mode, conversations.follow_up_mode, conversations.is_pinned, conversations.created_at, conversations.updated_at 
FROM conversations 
WHERE conversations.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT conversations.id, conversations.user_id, conversations.bucket_id, conversations.title, conversations.web_search_mode, conversations.follow_up_mode, conversations.is_pinned, conversations.created_at, conversations.updated_at 
FROM conversations 
WHERE conversations.id = $1::UUID
2026-04-06 02:14:11,422 INFO sqlalchemy.engine.Engine [generated in 0.00054s] (UUID('5bcce52f-2acd-44fe-b6f6-6a9ae7b6fb50'),)
INFO      sqlalchemy.engine.Engine                  [generated in 0.00054s] (UUID('5bcce52f-2acd-44fe-b6f6-6a9ae7b6fb50'),)
2026-04-06 02:14:11,423 INFO sqlalchemy.engine.Engine COMMIT
INFO      sqlalchemy.engine.Engine                  COMMIT
2026-04-06 02:14:11,428 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:14:11,429 INFO sqlalchemy.engine.Engine SELECT conversations.id, conversations.user_id, conversations.bucket_id, conversations.title, conversations.web_search_mode, conversations.follow_up_mode, conversations.is_pinned, conversations.created_at, conversations.updated_at 
FROM conversations 
WHERE conversations.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT conversations.id, conversations.user_id, conversations.bucket_id, conversations.title, conversations.web_search_mode, conversations.follow_up_mode, conversations.is_pinned, conversations.created_at, conversations.updated_at 
FROM conversations 
WHERE conversations.id = $1::UUID
2026-04-06 02:14:11,430 INFO sqlalchemy.engine.Engine [cached since 0.008406s ago] (UUID('64984f1b-3917-46f0-9555-e0ef067c040b'),)
INFO      sqlalchemy.engine.Engine                  [cached since 0.008406s ago] (UUID('64984f1b-3917-46f0-9555-e0ef067c040b'),)
2026-04-06 02:14:11,456 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:14:11,459 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:14:11,500 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:14:11,502 INFO sqlalchemy.engine.Engine SELECT conversations.id, conversations.user_id, conversations.bucket_id, conversations.title, conversations.web_search_mode, conversations.follow_up_mode, conversations.is_pinned, conversations.created_at, conversations.updated_at 
FROM conversations 
WHERE conversations.id = $1::UUID AND conversations.bucket_id = $2::UUID AND conversations.user_id = $3::UUID
INFO      sqlalchemy.engine.Engine                  SELECT conversations.id, conversations.user_id, conversations.bucket_id, conversations.title, conversations.web_search_mode, conversations.follow_up_mode, conversations.is_pinned, conversations.created_at, conversations.updated_at 
FROM conversations 
WHERE conversations.id = $1::UUID AND conversations.bucket_id = $2::UUID AND conversations.user_id = $3::UUID
2026-04-06 02:14:11,502 INFO sqlalchemy.engine.Engine [generated in 0.00054s] (UUID('5bcce52f-2acd-44fe-b6f6-6a9ae7b6fb50'), UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'), UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'))
INFO      sqlalchemy.engine.Engine                  [generated in 0.00054s] (UUID('5bcce52f-2acd-44fe-b6f6-6a9ae7b6fb50'), UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'), UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'))
2026-04-06 02:14:11,510 INFO sqlalchemy.engine.Engine SELECT messages.id, messages.conversation_id, messages.parent_message_id, messages.role, messages.content, messages.chunks_used, messages.token_count, messages.embedding_status, messages.agent_wrote_file_id, messages.created_at 
FROM messages 
WHERE messages.conversation_id = $1::UUID ORDER BY messages.created_at ASC
INFO      sqlalchemy.engine.Engine                  SELECT messages.id, messages.conversation_id, messages.parent_message_id, messages.role, messages.content, messages.chunks_used, messages.token_count, messages.embedding_status, messages.agent_wrote_file_id, messages.created_at 
FROM messages 
WHERE messages.conversation_id = $1::UUID ORDER BY messages.created_at ASC
2026-04-06 02:14:11,511 INFO sqlalchemy.engine.Engine [generated in 0.00058s] (UUID('5bcce52f-2acd-44fe-b6f6-6a9ae7b6fb50'),)
INFO      sqlalchemy.engine.Engine                  [generated in 0.00058s] (UUID('5bcce52f-2acd-44fe-b6f6-6a9ae7b6fb50'),)
2026-04-06 02:14:11,512 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:14:11,512 INFO sqlalchemy.engine.Engine SELECT conversations.id, conversations.user_id, conversations.bucket_id, conversations.title, conversations.web_search_mode, conversations.follow_up_mode, conversations.is_pinned, conversations.created_at, conversations.updated_at 
FROM conversations 
WHERE conversations.id = $1::UUID AND conversations.bucket_id = $2::UUID AND conversations.user_id = $3::UUID
INFO      sqlalchemy.engine.Engine                  SELECT conversations.id, conversations.user_id, conversations.bucket_id, conversations.title, conversations.web_search_mode, conversations.follow_up_mode, conversations.is_pinned, conversations.created_at, conversations.updated_at 
FROM conversations 
WHERE conversations.id = $1::UUID AND conversations.bucket_id = $2::UUID AND conversations.user_id = $3::UUID
2026-04-06 02:14:11,513 INFO sqlalchemy.engine.Engine [cached since 0.0113s ago] (UUID('64984f1b-3917-46f0-9555-e0ef067c040b'), UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'), UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'))
INFO      sqlalchemy.engine.Engine                  [cached since 0.0113s ago] (UUID('64984f1b-3917-46f0-9555-e0ef067c040b'), UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'), UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'))
2026-04-06 02:14:11,516 INFO sqlalchemy.engine.Engine SELECT messages.id, messages.conversation_id, messages.parent_message_id, messages.role, messages.content, messages.chunks_used, messages.token_count, messages.embedding_status, messages.agent_wrote_file_id, messages.created_at 
FROM messages 
WHERE messages.conversation_id = $1::UUID ORDER BY messages.created_at ASC
INFO      sqlalchemy.engine.Engine                  SELECT messages.id, messages.conversation_id, messages.parent_message_id, messages.role, messages.content, messages.chunks_used, messages.token_count, messages.embedding_status, messages.agent_wrote_file_id, messages.created_at 
FROM messages 
WHERE messages.conversation_id = $1::UUID ORDER BY messages.created_at ASC
2026-04-06 02:14:11,517 INFO sqlalchemy.engine.Engine [cached since 0.006493s ago] (UUID('64984f1b-3917-46f0-9555-e0ef067c040b'),)
INFO      sqlalchemy.engine.Engine                  [cached since 0.006493s ago] (UUID('64984f1b-3917-46f0-9555-e0ef067c040b'),)
2026-04-06 02:14:11,525 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:14:11,528 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
DEBUG     python_multipart.multipart                Calling on_part_begin with no data
DEBUG     python_multipart.multipart                Calling on_header_field with data[42:61]
DEBUG     python_multipart.multipart                Calling on_header_value with data[63:144]
DEBUG     python_multipart.multipart                Calling on_header_end with no data
DEBUG     python_multipart.multipart                Calling on_header_field with data[146:158]
DEBUG     python_multipart.multipart                Calling on_header_value with data[160:173]
DEBUG     python_multipart.multipart                Calling on_header_end with no data
DEBUG     python_multipart.multipart                Calling on_headers_finished with no data
DEBUG     python_multipart.multipart                Calling on_part_data with data[177:12618]
DEBUG     python_multipart.multipart                Calling on_part_data with data[0:8412]
DEBUG     python_multipart.multipart                Calling on_part_data with data[0:18226]
DEBUG     python_multipart.multipart                Calling on_part_data with data[0:16824]
DEBUG     python_multipart.multipart                Calling on_part_data with data[0:9814]
DEBUG     python_multipart.multipart                Calling on_part_data with data[0:4911]
DEBUG     python_multipart.multipart                Calling on_part_end with no data
DEBUG     python_multipart.multipart                Calling on_end with no data
2026-04-06 02:14:24,843 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:14:24,844 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:14:24,844 INFO sqlalchemy.engine.Engine [cached since 13.64s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 13.64s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
DEBUG     botocore.hooks                            Changing event name from creating-client-class.iot-data to creating-client-class.iot-data-plane
DEBUG     botocore.hooks                            Changing event name from before-call.apigateway to before-call.api-gateway
DEBUG     botocore.hooks                            Changing event name from request-created.machinelearning.Predict to request-created.machine-learning.Predict
DEBUG     botocore.hooks                            Changing event name from before-parameter-build.autoscaling.CreateLaunchConfiguration to before-parameter-build.auto-scaling.CreateLaunchConfiguration
DEBUG     botocore.hooks                            Changing event name from before-parameter-build.route53 to before-parameter-build.route-53
DEBUG     botocore.hooks                            Changing event name from request-created.cloudsearchdomain.Search to request-created.cloudsearch-domain.Search
DEBUG     botocore.hooks                            Changing event name from docs.*.autoscaling.CreateLaunchConfiguration.complete-section to docs.*.auto-scaling.CreateLaunchConfiguration.complete-section
DEBUG     botocore.hooks                            Changing event name from before-parameter-build.logs.CreateExportTask to before-parameter-build.cloudwatch-logs.CreateExportTask
DEBUG     botocore.hooks                            Changing event name from docs.*.logs.CreateExportTask.complete-section to docs.*.cloudwatch-logs.CreateExportTask.complete-section
DEBUG     botocore.hooks                            Changing event name from before-parameter-build.cloudsearchdomain.Search to before-parameter-build.cloudsearch-domain.Search
DEBUG     botocore.hooks                            Changing event name from docs.*.cloudsearchdomain.Search.complete-section to docs.*.cloudsearch-domain.Search.complete-section
DEBUG     botocore.loaders                          Loading JSON file: /home/chaffanjutt/AIVEILIX/backend/.venv/lib/python3.10/site-packages/botocore/data/endpoints.json
DEBUG     botocore.loaders                          Loading JSON file: /home/chaffanjutt/AIVEILIX/backend/.venv/lib/python3.10/site-packages/botocore/data/sdk-default-configuration.json
DEBUG     botocore.hooks                            Event choose-service-name: calling handler <function handle_service_name_alias at 0x75202a078040>
DEBUG     botocore.loaders                          Loading JSON file: /home/chaffanjutt/AIVEILIX/backend/.venv/lib/python3.10/site-packages/botocore/data/s3/2006-03-01/service-2.json.gz
DEBUG     botocore.loaders                          Loading JSON file: /home/chaffanjutt/AIVEILIX/backend/.venv/lib/python3.10/site-packages/botocore/data/s3/2006-03-01/service-2.sdk-extras.json
DEBUG     botocore.loaders                          Loading JSON file: /home/chaffanjutt/AIVEILIX/backend/.venv/lib/python3.10/site-packages/botocore/data/s3/2006-03-01/endpoint-rule-set-1.json.gz
DEBUG     botocore.loaders                          Loading JSON file: /home/chaffanjutt/AIVEILIX/backend/.venv/lib/python3.10/site-packages/botocore/data/partitions.json
DEBUG     botocore.hooks                            Event creating-client-class.s3: calling handler <function add_generate_presigned_post at 0x75202a1d1a20>
DEBUG     botocore.hooks                            Event creating-client-class.s3: calling handler <function lazy_call.<locals>._handler at 0x751f5a9fca60>
DEBUG     botocore.hooks                            Event creating-client-class.s3: calling handler <function add_generate_presigned_url at 0x75202a1d17e0>
DEBUG     botocore.regions                          Creating a regex based endpoint for s3, auto
DEBUG     botocore.endpoint                         Setting s3 timeout as (60, 60)
DEBUG     botocore.loaders                          Loading JSON file: /home/chaffanjutt/AIVEILIX/backend/.venv/lib/python3.10/site-packages/botocore/data/_retry.json
DEBUG     botocore.client                           Registering retry handlers for service: s3
DEBUG     botocore.utils                            Registering S3 region redirector handler
DEBUG     botocore.utils                            Registering S3Express Identity Resolver
DEBUG     boto3.s3.transfer                         Opting out of CRT Transfer Manager. Preferred client: auto, CRT available: False, Instance Optimized: False.
DEBUG     boto3.s3.transfer                         Using default client. pid: 18943, thread: 128781249298432
DEBUG     s3transfer.utils                          Acquiring 0
DEBUG     s3transfer.tasks                          UploadSubmissionTask(transfer_id=0, {'transfer_future': <s3transfer.futures.TransferFuture object at 0x751f59e828f0>}) about to wait for the following futures []
DEBUG     s3transfer.tasks                          UploadSubmissionTask(transfer_id=0, {'transfer_future': <s3transfer.futures.TransferFuture object at 0x751f59e828f0>}) done waiting for dependent futures
DEBUG     s3transfer.tasks                          Executing task UploadSubmissionTask(transfer_id=0, {'transfer_future': <s3transfer.futures.TransferFuture object at 0x751f59e828f0>}) with kwargs {'client': <botocore.client.S3 object at 0x751f59f9d360>, 'config': <boto3.s3.transfer.TransferConfig object at 0x751f5a9641f0>, 'osutil': <s3transfer.utils.OSUtils object at 0x751f59e81f00>, 'request_executor': <s3transfer.futures.BoundedExecutor object at 0x751f59e820e0>, 'transfer_future': <s3transfer.futures.TransferFuture object at 0x751f59e828f0>}
DEBUG     s3transfer.futures                        Submitting task PutObjectTask(transfer_id=0, {'bucket': 'aiveilix', 'key': 'raw/1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7/v1/BOTUVIC_v1.0_Product_Specification_UPDATED.md', 'extra_args': {'ContentType': 'text/markdown'}}) to executor <s3transfer.futures.BoundedExecutor object at 0x751f59e820e0> for transfer request: 0.
DEBUG     s3transfer.utils                          Acquiring 0
DEBUG     s3transfer.tasks                          PutObjectTask(transfer_id=0, {'bucket': 'aiveilix', 'key': 'raw/1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7/v1/BOTUVIC_v1.0_Product_Specification_UPDATED.md', 'extra_args': {'ContentType': 'text/markdown'}}) about to wait for the following futures []
DEBUG     s3transfer.utils                          Releasing acquire 0/None
DEBUG     s3transfer.tasks                          PutObjectTask(transfer_id=0, {'bucket': 'aiveilix', 'key': 'raw/1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7/v1/BOTUVIC_v1.0_Product_Specification_UPDATED.md', 'extra_args': {'ContentType': 'text/markdown'}}) done waiting for dependent futures
DEBUG     s3transfer.tasks                          Executing task PutObjectTask(transfer_id=0, {'bucket': 'aiveilix', 'key': 'raw/1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7/v1/BOTUVIC_v1.0_Product_Specification_UPDATED.md', 'extra_args': {'ContentType': 'text/markdown'}}) with kwargs {'client': <botocore.client.S3 object at 0x751f59f9d360>, 'fileobj': <s3transfer.utils.ReadFileChunk object at 0x751f59e82e00>, 'bucket': 'aiveilix', 'key': 'raw/1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7/v1/BOTUVIC_v1.0_Product_Specification_UPDATED.md', 'extra_args': {'ContentType': 'text/markdown'}}
DEBUG     botocore.hooks                            Event before-parameter-build.s3.PutObject: calling handler <function validate_ascii_metadata at 0x75202a07a5f0>
DEBUG     botocore.hooks                            Event before-parameter-build.s3.PutObject: calling handler <function sse_md5 at 0x75202a079a20>
DEBUG     botocore.hooks                            Event before-parameter-build.s3.PutObject: calling handler <function convert_body_to_file_like_object at 0x75202a07aef0>
DEBUG     botocore.hooks                            Event before-parameter-build.s3.PutObject: calling handler <function validate_bucket_name at 0x75202a079990>
DEBUG     botocore.hooks                            Event before-parameter-build.s3.PutObject: calling handler <function remove_bucket_from_url_paths_from_model at 0x75202a07b7f0>
DEBUG     botocore.hooks                            Event before-parameter-build.s3.PutObject: calling handler <bound method S3RegionRedirectorv2.annotate_request_context of <botocore.utils.S3RegionRedirectorv2 object at 0x751f59e81e10>>
DEBUG     botocore.hooks                            Event before-parameter-build.s3.PutObject: calling handler <bound method ClientCreator._inject_s3_input_parameters of <botocore.client.ClientCreator object at 0x751f5a967130>>
DEBUG     botocore.hooks                            Event before-parameter-build.s3.PutObject: calling handler <function generate_idempotent_uuid at 0x75202a0797e0>
DEBUG     botocore.hooks                            Event before-endpoint-resolution.s3: calling handler <function customize_endpoint_resolver_builtins at 0x75202a07b9a0>
DEBUG     botocore.hooks                            Event before-endpoint-resolution.s3: calling handler <bound method S3RegionRedirectorv2.redirect_from_cache of <botocore.utils.S3RegionRedirectorv2 object at 0x751f59e81e10>>
DEBUG     botocore.regions                          Calling endpoint provider with parameters: {'Bucket': 'aiveilix', 'Region': 'auto', 'UseFIPS': False, 'UseDualStack': False, 'Endpoint': 'https://93d07d6cff38141aaf5eed882cda6725.r2.cloudflarestorage.com', 'ForcePathStyle': True, 'Accelerate': False, 'UseGlobalEndpoint': False, 'Key': 'raw/1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7/v1/BOTUVIC_v1.0_Product_Specification_UPDATED.md', 'DisableMultiRegionAccessPoints': False, 'UseArnRegion': True}
DEBUG     botocore.regions                          Endpoint provider result: https://93d07d6cff38141aaf5eed882cda6725.r2.cloudflarestorage.com/aiveilix
DEBUG     botocore.regions                          Selecting from endpoint provider's list of auth schemes: "sigv4". User selected auth scheme is: "None"
DEBUG     botocore.regions                          Selected auth type "v4" as "v4" with signing context params: {'region': 'auto', 'signing_name': 's3', 'disableDoubleEncoding': True}
DEBUG     botocore.hooks                            Event before-call.s3.PutObject: calling handler <function conditionally_calculate_checksum at 0x75202a124160>
DEBUG     botocore.hooks                            Event before-call.s3.PutObject: calling handler <function add_expect_header at 0x75202a079cf0>
DEBUG     botocore.handlers                         Adding expect 100 continue header to request.
DEBUG     botocore.hooks                            Event before-call.s3.PutObject: calling handler <bound method S3ExpressIdentityResolver.apply_signing_cache_key of <botocore.utils.S3ExpressIdentityResolver object at 0x751f59e81e70>>
DEBUG     botocore.hooks                            Event before-call.s3.PutObject: calling handler <function add_recursion_detection_header at 0x75202a0793f0>
DEBUG     botocore.hooks                            Event before-call.s3.PutObject: calling handler <function add_query_compatibility_header at 0x75202a07be20>
DEBUG     botocore.hooks                            Event before-call.s3.PutObject: calling handler <function inject_api_version_header_if_needed at 0x75202a07b010>
DEBUG     botocore.endpoint                         Making request for OperationModel(name=PutObject) with params: {'url_path': '/raw/1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7/v1/BOTUVIC_v1.0_Product_Specification_UPDATED.md', 'query_string': {}, 'method': 'PUT', 'headers': {'Content-Type': 'text/markdown', 'User-Agent': 'Boto3/1.35.85 md/Botocore#1.35.99 ua/2.0 os/linux#6.8.0-1048-gcp md/arch#x86_64 lang/python#3.10.12 md/pyimpl#CPython cfg/retry-mode#legacy Botocore/1.35.99', 'Content-MD5': 'F0Q6h+PYn5ZNoBUfRo+ueQ==', 'Expect': '100-continue'}, 'body': <s3transfer.utils.ReadFileChunk object at 0x751f59e82e00>, 'auth_path': '/aiveilix/raw/1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7/v1/BOTUVIC_v1.0_Product_Specification_UPDATED.md', 'url': 'https://93d07d6cff38141aaf5eed882cda6725.r2.cloudflarestorage.com/aiveilix/raw/1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7/v1/BOTUVIC_v1.0_Product_Specification_UPDATED.md', 'context': {'client_region': 'auto', 'client_config': <botocore.config.Config object at 0x751f59e360b0>, 'has_streaming_input': True, 'auth_type': 'v4', 'unsigned_payload': None, 's3_redirect': {'redirected': False, 'bucket': 'aiveilix', 'params': {'Bucket': 'aiveilix', 'Key': 'raw/1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7/v1/BOTUVIC_v1.0_Product_Specification_UPDATED.md', 'Body': <s3transfer.utils.ReadFileChunk object at 0x751f59e82e00>, 'ContentType': 'text/markdown'}}, 'input_params': {'Bucket': 'aiveilix', 'Key': 'raw/1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7/v1/BOTUVIC_v1.0_Product_Specification_UPDATED.md'}, 'signing': {'region': 'auto', 'signing_name': 's3', 'disableDoubleEncoding': True}, 'endpoint_properties': {'authSchemes': [{'disableDoubleEncoding': True, 'name': 'sigv4', 'signingName': 's3', 'signingRegion': 'auto'}]}}}
DEBUG     botocore.hooks                            Event request-created.s3.PutObject: calling handler <function signal_not_transferring at 0x751f59ff8ca0>
DEBUG     botocore.hooks                            Event request-created.s3.PutObject: calling handler <bound method RequestSigner.handler of <botocore.signers.RequestSigner object at 0x751f59f9db40>>
DEBUG     botocore.hooks                            Event choose-signer.s3.PutObject: calling handler <function set_operation_specific_signer at 0x75202a079630>
DEBUG     botocore.hooks                            Event before-sign.s3.PutObject: calling handler <function remove_arn_from_signing_path at 0x75202a07b910>
DEBUG     botocore.hooks                            Event before-sign.s3.PutObject: calling handler <bound method S3ExpressIdentityResolver.resolve_s3express_identity of <botocore.utils.S3ExpressIdentityResolver object at 0x751f59e81e70>>
DEBUG     botocore.auth                             Calculating signature using v4 auth.
DEBUG     botocore.auth                             CanonicalRequest:
PUT
/aiveilix/raw/1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7/v1/BOTUVIC_v1.0_Product_Specification_UPDATED.md

content-md5:F0Q6h+PYn5ZNoBUfRo+ueQ==
content-type:text/markdown
host:93d07d6cff38141aaf5eed882cda6725.r2.cloudflarestorage.com
x-amz-content-sha256:UNSIGNED-PAYLOAD
x-amz-date:20260406T021425Z

content-md5;content-type;host;x-amz-content-sha256;x-amz-date
UNSIGNED-PAYLOAD
DEBUG     botocore.auth                             StringToSign:
AWS4-HMAC-SHA256
20260406T021425Z
20260406/auto/s3/aws4_request
9960ca8f88efbe978ab20a7833f086a803adac3a75029f1a55056af6ade303c5
DEBUG     botocore.auth                             Signature:
77cea335597826eb1717d3d0e2464003a26ec26d81154377075be15c4ccc5050
DEBUG     botocore.hooks                            Event request-created.s3.PutObject: calling handler <function signal_transferring at 0x751f59ff8d30>
DEBUG     botocore.hooks                            Event request-created.s3.PutObject: calling handler <function add_retry_headers at 0x75202a07b760>
DEBUG     botocore.endpoint                         Sending http request: <AWSPreparedRequest stream_output=False, method=PUT, url=https://93d07d6cff38141aaf5eed882cda6725.r2.cloudflarestorage.com/aiveilix/raw/1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7/v1/BOTUVIC_v1.0_Product_Specification_UPDATED.md, headers={'Content-Type': b'text/markdown', 'User-Agent': b'Boto3/1.35.85 md/Botocore#1.35.99 ua/2.0 os/linux#6.8.0-1048-gcp md/arch#x86_64 lang/python#3.10.12 md/pyimpl#CPython cfg/retry-mode#legacy Botocore/1.35.99', 'Content-MD5': b'F0Q6h+PYn5ZNoBUfRo+ueQ==', 'Expect': b'100-continue', 'X-Amz-Date': b'20260406T021425Z', 'X-Amz-Content-SHA256': b'UNSIGNED-PAYLOAD', 'Authorization': b'AWS4-HMAC-SHA256 Credential=a14d95abb63a7791c665f6833e04b1ea/20260406/auto/s3/aws4_request, SignedHeaders=content-md5;content-type;host;x-amz-content-sha256;x-amz-date, Signature=77cea335597826eb1717d3d0e2464003a26ec26d81154377075be15c4ccc5050', 'amz-sdk-invocation-id': b'41e47c36-d24f-4225-86ca-fca881572c50', 'amz-sdk-request': b'attempt=1', 'Content-Length': '70628'}>
DEBUG     botocore.httpsession                      Certificate path: /home/chaffanjutt/AIVEILIX/backend/.venv/lib/python3.10/site-packages/certifi/cacert.pem
DEBUG     urllib3.connectionpool                    Starting new HTTPS connection (1): 93d07d6cff38141aaf5eed882cda6725.r2.cloudflarestorage.com:443
DEBUG     botocore.awsrequest                       Waiting for 100 Continue response.
DEBUG     botocore.awsrequest                       100 Continue response seen, now sending request body.
DEBUG     urllib3.connectionpool                    https://93d07d6cff38141aaf5eed882cda6725.r2.cloudflarestorage.com:443 "PUT /aiveilix/raw/1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7/v1/BOTUVIC_v1.0_Product_Specification_UPDATED.md HTTP/1.1" 200 0
DEBUG     botocore.hooks                            Event before-parse.s3.PutObject: calling handler <function _handle_200_error at 0x75202a07bc70>
DEBUG     botocore.hooks                            Event before-parse.s3.PutObject: calling handler <function handle_expires_header at 0x75202a07bac0>
DEBUG     botocore.parsers                          Response headers: {'Date': 'Mon, 06 Apr 2026 02:14:25 GMT', 'Content-Type': 'text/plain;charset=UTF-8', 'Content-Length': '0', 'Connection': 'keep-alive', 'ETag': '"17443a87e3d89f964da0151f468fae79"', 'x-amz-checksum-crc64nvme': 'lMeA0KfXsjM=', 'x-amz-version-id': '7e629f6e21f3110dc80b35d16a098413', 'Vary': 'Accept-Encoding', 'Server': 'cloudflare', 'CF-RAY': '9e7d47690fea3f22-NRT'}
DEBUG     botocore.parsers                          Response body:
b''
DEBUG     botocore.hooks                            Event needs-retry.s3.PutObject: calling handler <function _update_status_code at 0x75202a07bd90>
DEBUG     botocore.hooks                            Event needs-retry.s3.PutObject: calling handler <botocore.retryhandler.RetryHandler object at 0x751f59e81d50>
DEBUG     botocore.retryhandler                     No retry needed.
DEBUG     botocore.hooks                            Event needs-retry.s3.PutObject: calling handler <bound method S3RegionRedirectorv2.redirect_from_error of <botocore.utils.S3RegionRedirectorv2 object at 0x751f59e81e10>>
DEBUG     s3transfer.utils                          Releasing acquire 0/None
INFO      app.services.storage.r2                   R2 upload OK: raw/1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7/v1/BOTUVIC_v1.0_Product_Specification_UPDATED.md
INFO      app.services.pipeline.upload              R2 upload complete: raw/1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7/v1/BOTUVIC_v1.0_Product_Specification_UPDATED.md
2026-04-06 02:14:25,686 INFO sqlalchemy.engine.Engine INSERT INTO files (id, bucket_id, user_id, category_id, name, type, size, r2_path, layout_json_path, status, page_count, version, is_agent_written) VALUES ($1::UUID, $2::UUID, $3::UUID, $4::UUID, $5::VARCHAR, $6::VARCHAR, $7::BIGINT, $8::VARCHAR, $9::VARCHAR, $10::file_status, $11::INTEGER, $12::INTEGER, $13::BOOLEAN) RETURNING files.created_at, files.updated_at
INFO      sqlalchemy.engine.Engine                  INSERT INTO files (id, bucket_id, user_id, category_id, name, type, size, r2_path, layout_json_path, status, page_count, version, is_agent_written) VALUES ($1::UUID, $2::UUID, $3::UUID, $4::UUID, $5::VARCHAR, $6::VARCHAR, $7::BIGINT, $8::VARCHAR, $9::VARCHAR, $10::file_status, $11::INTEGER, $12::INTEGER, $13::BOOLEAN) RETURNING files.created_at, files.updated_at
2026-04-06 02:14:25,686 INFO sqlalchemy.engine.Engine [generated in 0.00100s] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'), UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'), UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), None, 'BOTUVIC_v1.0_Product_Specification_UPDATED.md', 'md', 70628, 'raw/1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7/v1/BOTUVIC_v1.0_Product_Specification_UPDATED.md', None, 'uploading', 0, 1, False)
INFO      sqlalchemy.engine.Engine                  [generated in 0.00100s] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'), UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'), UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), None, 'BOTUVIC_v1.0_Product_Specification_UPDATED.md', 'md', 70628, 'raw/1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7/v1/BOTUVIC_v1.0_Product_Specification_UPDATED.md', None, 'uploading', 0, 1, False)
2026-04-06 02:14:25,698 INFO sqlalchemy.engine.Engine INSERT INTO file_versions (id, file_id, version_number, r2_path, size) VALUES ($1::UUID, $2::UUID, $3::INTEGER, $4::VARCHAR, $5::BIGINT) RETURNING file_versions.created_at
INFO      sqlalchemy.engine.Engine                  INSERT INTO file_versions (id, file_id, version_number, r2_path, size) VALUES ($1::UUID, $2::UUID, $3::INTEGER, $4::VARCHAR, $5::BIGINT) RETURNING file_versions.created_at
2026-04-06 02:14:25,699 INFO sqlalchemy.engine.Engine [generated in 0.00194s] (UUID('82ddb123-e536-4f45-b87e-a4ae0a6e2934'), UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'), 1, 'raw/1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7/v1/BOTUVIC_v1.0_Product_Specification_UPDATED.md', 70628)
INFO      sqlalchemy.engine.Engine                  [generated in 0.00194s] (UUID('82ddb123-e536-4f45-b87e-a4ae0a6e2934'), UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'), 1, 'raw/1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7/v1/BOTUVIC_v1.0_Product_Specification_UPDATED.md', 70628)
2026-04-06 02:14:25,706 INFO sqlalchemy.engine.Engine INSERT INTO investigation_events (id, file_id, event, status, metadata) VALUES ($1::UUID, $2::UUID, $3::VARCHAR, $4::event_status, $5::JSONB) RETURNING investigation_events.created_at
INFO      sqlalchemy.engine.Engine                  INSERT INTO investigation_events (id, file_id, event, status, metadata) VALUES ($1::UUID, $2::UUID, $3::VARCHAR, $4::event_status, $5::JSONB) RETURNING investigation_events.created_at
2026-04-06 02:14:25,706 INFO sqlalchemy.engine.Engine [generated in 0.00143s] (UUID('517646d9-a50e-4673-abb6-d88d74b5c2cd'), UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'), 'upload_completed', 'completed', '{"filename": "BOTUVIC_v1.0_Product_Specification_UPDATED.md", "size": 70628, "r2_path": "raw/1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7/v1/BOTUVIC_v1.0_Product_Specification_UPDATED.md", "trace_run_id": "d313c038-8766-431e-848d-542087af1456", "trigger_source": "upload", "stage": "upload_intake"}')
INFO      sqlalchemy.engine.Engine                  [generated in 0.00143s] (UUID('517646d9-a50e-4673-abb6-d88d74b5c2cd'), UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'), 'upload_completed', 'completed', '{"filename": "BOTUVIC_v1.0_Product_Specification_UPDATED.md", "size": 70628, "r2_path": "raw/1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7/v1/BOTUVIC_v1.0_Product_Specification_UPDATED.md", "trace_run_id": "d313c038-8766-431e-848d-542087af1456", "trigger_source": "upload", "stage": "upload_intake"}')
2026-04-06 02:14:25,739 INFO sqlalchemy.engine.Engine UPDATE files SET status=$1::file_status, updated_at=now() WHERE files.id = $2::UUID
INFO      sqlalchemy.engine.Engine                  UPDATE files SET status=$1::file_status, updated_at=now() WHERE files.id = $2::UUID
2026-04-06 02:14:25,740 INFO sqlalchemy.engine.Engine [generated in 0.00059s] ('processing', UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'))
INFO      sqlalchemy.engine.Engine                  [generated in 0.00059s] ('processing', UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'))
2026-04-06 02:14:25,744 INFO sqlalchemy.engine.Engine INSERT INTO investigation_events (id, file_id, event, status, metadata) VALUES ($1::UUID, $2::UUID, $3::VARCHAR, $4::event_status, $5::JSONB) RETURNING investigation_events.created_at
INFO      sqlalchemy.engine.Engine                  INSERT INTO investigation_events (id, file_id, event, status, metadata) VALUES ($1::UUID, $2::UUID, $3::VARCHAR, $4::event_status, $5::JSONB) RETURNING investigation_events.created_at
2026-04-06 02:14:25,744 INFO sqlalchemy.engine.Engine [cached since 0.03934s ago] (UUID('5c2ce1f2-99ab-4cbb-8736-5aaed20b9b93'), UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'), 'file_processing_started', 'started', '{"trace_run_id": "d313c038-8766-431e-848d-542087af1456", "trigger_source": "upload", "stage": "pipeline_enqueue"}')
INFO      sqlalchemy.engine.Engine                  [cached since 0.03934s ago] (UUID('5c2ce1f2-99ab-4cbb-8736-5aaed20b9b93'), UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'), 'file_processing_started', 'started', '{"trace_run_id": "d313c038-8766-431e-848d-542087af1456", "trigger_source": "upload", "stage": "pipeline_enqueue"}')
2026-04-06 02:14:25,746 INFO sqlalchemy.engine.Engine COMMIT
INFO      sqlalchemy.engine.Engine                  COMMIT
2026-04-06 02:14:25,752 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:14:25,754 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.id = $1::UUID
2026-04-06 02:14:25,754 INFO sqlalchemy.engine.Engine [generated in 0.00047s] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
INFO      sqlalchemy.engine.Engine                  [generated in 0.00047s] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
2026-04-06 02:14:25,763 INFO sqlalchemy.engine.Engine INSERT INTO notifications (id, user_id, type, title, message, is_read) VALUES ($1::UUID, $2::UUID, $3::notification_type, $4::VARCHAR, $5::VARCHAR, $6::BOOLEAN) RETURNING notifications.created_at
INFO      sqlalchemy.engine.Engine                  INSERT INTO notifications (id, user_id, type, title, message, is_read) VALUES ($1::UUID, $2::UUID, $3::notification_type, $4::VARCHAR, $5::VARCHAR, $6::BOOLEAN) RETURNING notifications.created_at
2026-04-06 02:14:25,764 INFO sqlalchemy.engine.Engine [cached since 25.39s ago] (UUID('d59696af-798d-442a-99e0-5df04dd07442'), UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), 'info', 'File upload started', '"BOTUVIC_v1.0_Product_Specification_UPDATED.md" was uploaded to "its for " and is now processing.', False)
INFO      sqlalchemy.engine.Engine                  [cached since 25.39s ago] (UUID('d59696af-798d-442a-99e0-5df04dd07442'), UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), 'info', 'File upload started', '"BOTUVIC_v1.0_Product_Specification_UPDATED.md" was uploaded to "its for " and is now processing.', False)
2026-04-06 02:14:25,765 INFO sqlalchemy.engine.Engine COMMIT
INFO      sqlalchemy.engine.Engine                  COMMIT
2026-04-06 02:14:25,770 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:14:25,771 INFO sqlalchemy.engine.Engine SELECT notifications.id, notifications.user_id, notifications.type, notifications.title, notifications.message, notifications.is_read, notifications.created_at 
FROM notifications 
WHERE notifications.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT notifications.id, notifications.user_id, notifications.type, notifications.title, notifications.message, notifications.is_read, notifications.created_at 
FROM notifications 
WHERE notifications.id = $1::UUID
2026-04-06 02:14:25,771 INFO sqlalchemy.engine.Engine [cached since 25.36s ago] (UUID('d59696af-798d-442a-99e0-5df04dd07442'),)
INFO      sqlalchemy.engine.Engine                  [cached since 25.36s ago] (UUID('d59696af-798d-442a-99e0-5df04dd07442'),)
2026-04-06 02:14:25,774 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:14:25,777 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:14:25,778 INFO sqlalchemy.engine.Engine INSERT INTO investigation_events (id, file_id, event, status, metadata) VALUES ($1::UUID, $2::UUID, $3::VARCHAR, $4::event_status, $5::JSONB) RETURNING investigation_events.created_at
INFO      sqlalchemy.engine.Engine                  INSERT INTO investigation_events (id, file_id, event, status, metadata) VALUES ($1::UUID, $2::UUID, $3::VARCHAR, $4::event_status, $5::JSONB) RETURNING investigation_events.created_at
2026-04-06 02:14:25,779 INFO sqlalchemy.engine.Engine [cached since 0.07365s ago] (UUID('0ffa2596-de20-4703-84f9-3e20275a43ef'), UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'), 'pipeline_run_started', 'started', '{"trace_run_id": "d313c038-8766-431e-848d-542087af1456", "trigger_source": "upload", "stage": "pipeline_run", "sequence": 1, "recorded_at": "2026-04-06T02:14:25.775895+00:00"}')
INFO      sqlalchemy.engine.Engine                  [cached since 0.07365s ago] (UUID('0ffa2596-de20-4703-84f9-3e20275a43ef'), UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'), 'pipeline_run_started', 'started', '{"trace_run_id": "d313c038-8766-431e-848d-542087af1456", "trigger_source": "upload", "stage": "pipeline_run", "sequence": 1, "recorded_at": "2026-04-06T02:14:25.775895+00:00"}')
2026-04-06 02:14:25,788 INFO sqlalchemy.engine.Engine COMMIT
INFO      sqlalchemy.engine.Engine                  COMMIT
INFO      app.services.pipeline.orchestrator        pipeline_trace file=1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7 trace=d313c038-8766-431e-848d-542087af1456 event=pipeline_run_started stage=pipeline_run status=started metadata={'trace_run_id': 'd313c038-8766-431e-848d-542087af1456', 'trigger_source': 'upload', 'stage': 'pipeline_run', 'sequence': 1, 'recorded_at': '2026-04-06T02:14:25.775895+00:00'}
2026-04-06 02:14:25,794 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:14:25,795 INFO sqlalchemy.engine.Engine SELECT pg_try_advisory_lock($1) AS acquired
INFO      sqlalchemy.engine.Engine                  SELECT pg_try_advisory_lock($1) AS acquired
2026-04-06 02:14:25,796 INFO sqlalchemy.engine.Engine [generated in 0.00058s] (2286455389110225403,)
INFO      sqlalchemy.engine.Engine                  [generated in 0.00058s] (2286455389110225403,)
2026-04-06 02:14:25,800 INFO sqlalchemy.engine.Engine SELECT files.id AS files_id, files.bucket_id AS files_bucket_id, files.user_id AS files_user_id, files.category_id AS files_category_id, files.name AS files_name, files.type AS files_type, files.size AS files_size, files.r2_path AS files_r2_path, files.layout_json_path AS files_layout_json_path, files.status AS files_status, files.page_count AS files_page_count, files.version AS files_version, files.is_agent_written AS files_is_agent_written, files.created_at AS files_created_at, files.updated_at AS files_updated_at 
FROM files 
WHERE files.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT files.id AS files_id, files.bucket_id AS files_bucket_id, files.user_id AS files_user_id, files.category_id AS files_category_id, files.name AS files_name, files.type AS files_type, files.size AS files_size, files.r2_path AS files_r2_path, files.layout_json_path AS files_layout_json_path, files.status AS files_status, files.page_count AS files_page_count, files.version AS files_version, files.is_agent_written AS files_is_agent_written, files.created_at AS files_created_at, files.updated_at AS files_updated_at 
FROM files 
WHERE files.id = $1::UUID
2026-04-06 02:14:25,801 INFO sqlalchemy.engine.Engine [generated in 0.00058s] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
INFO      sqlalchemy.engine.Engine                  [generated in 0.00058s] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
2026-04-06 02:14:25,806 INFO sqlalchemy.engine.Engine UPDATE files SET status=$1::file_status, updated_at=now() WHERE files.id = $2::UUID
INFO      sqlalchemy.engine.Engine                  UPDATE files SET status=$1::file_status, updated_at=now() WHERE files.id = $2::UUID
2026-04-06 02:14:25,807 INFO sqlalchemy.engine.Engine [generated in 0.00058s] ('processing', UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'))
INFO      sqlalchemy.engine.Engine                  [generated in 0.00058s] ('processing', UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'))
2026-04-06 02:14:25,811 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:14:25,812 INFO sqlalchemy.engine.Engine INSERT INTO investigation_events (id, file_id, event, status, metadata) VALUES ($1::UUID, $2::UUID, $3::VARCHAR, $4::event_status, $5::JSONB) RETURNING investigation_events.created_at
INFO      sqlalchemy.engine.Engine                  INSERT INTO investigation_events (id, file_id, event, status, metadata) VALUES ($1::UUID, $2::UUID, $3::VARCHAR, $4::event_status, $5::JSONB) RETURNING investigation_events.created_at
2026-04-06 02:14:25,812 INFO sqlalchemy.engine.Engine [cached since 0.1074s ago] (UUID('e97cf04d-76f5-4885-aa39-c58fc93c8e0e'), UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'), 'vector_cleanup_started', 'started', '{"trace_run_id": "d313c038-8766-431e-848d-542087af1456", "trigger_source": "upload", "stage": "vector_cleanup", "sequence": 2, "recorded_at": "2026-04-06T02:14:25.809851+00:00"}')
INFO      sqlalchemy.engine.Engine                  [cached since 0.1074s ago] (UUID('e97cf04d-76f5-4885-aa39-c58fc93c8e0e'), UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'), 'vector_cleanup_started', 'started', '{"trace_run_id": "d313c038-8766-431e-848d-542087af1456", "trigger_source": "upload", "stage": "vector_cleanup", "sequence": 2, "recorded_at": "2026-04-06T02:14:25.809851+00:00"}')
2026-04-06 02:14:25,814 INFO sqlalchemy.engine.Engine COMMIT
INFO      sqlalchemy.engine.Engine                  COMMIT
INFO      app.services.pipeline.orchestrator        pipeline_trace file=1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7 trace=d313c038-8766-431e-848d-542087af1456 event=vector_cleanup_started stage=vector_cleanup status=started metadata={'trace_run_id': 'd313c038-8766-431e-848d-542087af1456', 'trigger_source': 'upload', 'stage': 'vector_cleanup', 'sequence': 2, 'recorded_at': '2026-04-06T02:14:25.809851+00:00'}
INFO      app.services.qdrant.file_indexer          Deprecated Qdrant vectors for file 1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7
2026-04-06 02:14:25,820 INFO sqlalchemy.engine.Engine DELETE FROM chunks WHERE chunks.file_id = $1::UUID
INFO      sqlalchemy.engine.Engine                  DELETE FROM chunks WHERE chunks.file_id = $1::UUID
2026-04-06 02:14:25,820 INFO sqlalchemy.engine.Engine [generated in 0.00062s] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
INFO      sqlalchemy.engine.Engine                  [generated in 0.00062s] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
2026-04-06 02:14:25,826 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:14:25,827 INFO sqlalchemy.engine.Engine INSERT INTO investigation_events (id, file_id, event, status, metadata) VALUES ($1::UUID, $2::UUID, $3::VARCHAR, $4::event_status, $5::JSONB) RETURNING investigation_events.created_at
INFO      sqlalchemy.engine.Engine                  INSERT INTO investigation_events (id, file_id, event, status, metadata) VALUES ($1::UUID, $2::UUID, $3::VARCHAR, $4::event_status, $5::JSONB) RETURNING investigation_events.created_at
2026-04-06 02:14:25,827 INFO sqlalchemy.engine.Engine [cached since 0.1219s ago] (UUID('bfdbedf9-dce8-4303-bac3-7fc7def5cf5c'), UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'), 'vector_cleanup_completed', 'completed', '{"trace_run_id": "d313c038-8766-431e-848d-542087af1456", "trigger_source": "upload", "stage": "vector_cleanup", "sequence": 3, "recorded_at": "2026-04-06T02:14:25.823450+00:00", "deleted_chunk_rows": "all_existing", "duration_ms": 13}')
INFO      sqlalchemy.engine.Engine                  [cached since 0.1219s ago] (UUID('bfdbedf9-dce8-4303-bac3-7fc7def5cf5c'), UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'), 'vector_cleanup_completed', 'completed', '{"trace_run_id": "d313c038-8766-431e-848d-542087af1456", "trigger_source": "upload", "stage": "vector_cleanup", "sequence": 3, "recorded_at": "2026-04-06T02:14:25.823450+00:00", "deleted_chunk_rows": "all_existing", "duration_ms": 13}')
2026-04-06 02:14:25,836 INFO sqlalchemy.engine.Engine COMMIT
INFO      sqlalchemy.engine.Engine                  COMMIT
INFO      app.services.pipeline.orchestrator        pipeline_trace file=1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7 trace=d313c038-8766-431e-848d-542087af1456 event=vector_cleanup_completed stage=vector_cleanup status=completed metadata={'trace_run_id': 'd313c038-8766-431e-848d-542087af1456', 'trigger_source': 'upload', 'stage': 'vector_cleanup', 'sequence': 3, 'recorded_at': '2026-04-06T02:14:25.823450+00:00', 'deleted_chunk_rows': 'all_existing', 'duration_ms': 13}
2026-04-06 02:14:25,842 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:14:25,843 INFO sqlalchemy.engine.Engine INSERT INTO investigation_events (id, file_id, event, status, metadata) VALUES ($1::UUID, $2::UUID, $3::VARCHAR, $4::event_status, $5::JSONB) RETURNING investigation_events.created_at
INFO      sqlalchemy.engine.Engine                  INSERT INTO investigation_events (id, file_id, event, status, metadata) VALUES ($1::UUID, $2::UUID, $3::VARCHAR, $4::event_status, $5::JSONB) RETURNING investigation_events.created_at
2026-04-06 02:14:25,843 INFO sqlalchemy.engine.Engine [cached since 0.1379s ago] (UUID('d785b798-93dc-4e93-b75b-ed938bc906e3'), UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'), 'download_started', 'started', '{"trace_run_id": "d313c038-8766-431e-848d-542087af1456", "trigger_source": "upload", "stage": "download", "sequence": 4, "recorded_at": "2026-04-06T02:14:25.840058+00:00"}')
INFO      sqlalchemy.engine.Engine                  [cached since 0.1379s ago] (UUID('d785b798-93dc-4e93-b75b-ed938bc906e3'), UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'), 'download_started', 'started', '{"trace_run_id": "d313c038-8766-431e-848d-542087af1456", "trigger_source": "upload", "stage": "download", "sequence": 4, "recorded_at": "2026-04-06T02:14:25.840058+00:00"}')
2026-04-06 02:14:25,867 INFO sqlalchemy.engine.Engine COMMIT
INFO      sqlalchemy.engine.Engine                  COMMIT
INFO      app.services.pipeline.orchestrator        pipeline_trace file=1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7 trace=d313c038-8766-431e-848d-542087af1456 event=download_started stage=download status=started metadata={'trace_run_id': 'd313c038-8766-431e-848d-542087af1456', 'trigger_source': 'upload', 'stage': 'download', 'sequence': 4, 'recorded_at': '2026-04-06T02:14:25.840058+00:00'}
DEBUG     boto3.s3.transfer                         Opting out of CRT Transfer Manager. Preferred client: auto, CRT available: False, Instance Optimized: False.
DEBUG     boto3.s3.transfer                         Using default client. pid: 18943, thread: 128781249298432
DEBUG     s3transfer.utils                          Acquiring 0
DEBUG     s3transfer.tasks                          DownloadSubmissionTask(transfer_id=0, {'transfer_future': <s3transfer.futures.TransferFuture object at 0x751f58d3ca00>}) about to wait for the following futures []
DEBUG     s3transfer.tasks                          DownloadSubmissionTask(transfer_id=0, {'transfer_future': <s3transfer.futures.TransferFuture object at 0x751f58d3ca00>}) done waiting for dependent futures
DEBUG     s3transfer.tasks                          Executing task DownloadSubmissionTask(transfer_id=0, {'transfer_future': <s3transfer.futures.TransferFuture object at 0x751f58d3ca00>}) with kwargs {'client': <botocore.client.S3 object at 0x751f59f9d360>, 'config': <boto3.s3.transfer.TransferConfig object at 0x751f59ee1660>, 'osutil': <s3transfer.utils.OSUtils object at 0x751f59ee1db0>, 'request_executor': <s3transfer.futures.BoundedExecutor object at 0x751f59ee27a0>, 'transfer_future': <s3transfer.futures.TransferFuture object at 0x751f58d3ca00>, 'io_executor': <s3transfer.futures.BoundedExecutor object at 0x751f58d3c1c0>}
DEBUG     botocore.hooks                            Event before-parameter-build.s3.HeadObject: calling handler <function sse_md5 at 0x75202a079a20>
DEBUG     botocore.hooks                            Event before-parameter-build.s3.HeadObject: calling handler <function validate_bucket_name at 0x75202a079990>
DEBUG     botocore.hooks                            Event before-parameter-build.s3.HeadObject: calling handler <function remove_bucket_from_url_paths_from_model at 0x75202a07b7f0>
DEBUG     botocore.hooks                            Event before-parameter-build.s3.HeadObject: calling handler <bound method S3RegionRedirectorv2.annotate_request_context of <botocore.utils.S3RegionRedirectorv2 object at 0x751f59e81e10>>
DEBUG     botocore.hooks                            Event before-parameter-build.s3.HeadObject: calling handler <bound method ClientCreator._inject_s3_input_parameters of <botocore.client.ClientCreator object at 0x751f5a967130>>
DEBUG     botocore.hooks                            Event before-parameter-build.s3.HeadObject: calling handler <function generate_idempotent_uuid at 0x75202a0797e0>
DEBUG     botocore.hooks                            Event before-endpoint-resolution.s3: calling handler <function customize_endpoint_resolver_builtins at 0x75202a07b9a0>
DEBUG     botocore.hooks                            Event before-endpoint-resolution.s3: calling handler <bound method S3RegionRedirectorv2.redirect_from_cache of <botocore.utils.S3RegionRedirectorv2 object at 0x751f59e81e10>>
DEBUG     botocore.regions                          Calling endpoint provider with parameters: {'Bucket': 'aiveilix', 'Region': 'auto', 'UseFIPS': False, 'UseDualStack': False, 'Endpoint': 'https://93d07d6cff38141aaf5eed882cda6725.r2.cloudflarestorage.com', 'ForcePathStyle': True, 'Accelerate': False, 'UseGlobalEndpoint': False, 'Key': 'raw/1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7/v1/BOTUVIC_v1.0_Product_Specification_UPDATED.md', 'DisableMultiRegionAccessPoints': False, 'UseArnRegion': True}
DEBUG     botocore.regions                          Endpoint provider result: https://93d07d6cff38141aaf5eed882cda6725.r2.cloudflarestorage.com/aiveilix
DEBUG     botocore.regions                          Selecting from endpoint provider's list of auth schemes: "sigv4". User selected auth scheme is: "None"
DEBUG     botocore.regions                          Selected auth type "v4" as "v4" with signing context params: {'region': 'auto', 'signing_name': 's3', 'disableDoubleEncoding': True}
DEBUG     botocore.hooks                            Event before-call.s3.HeadObject: calling handler <function add_expect_header at 0x75202a079cf0>
DEBUG     botocore.hooks                            Event before-call.s3.HeadObject: calling handler <bound method S3ExpressIdentityResolver.apply_signing_cache_key of <botocore.utils.S3ExpressIdentityResolver object at 0x751f59e81e70>>
DEBUG     botocore.hooks                            Event before-call.s3.HeadObject: calling handler <function add_recursion_detection_header at 0x75202a0793f0>
DEBUG     botocore.hooks                            Event before-call.s3.HeadObject: calling handler <function add_query_compatibility_header at 0x75202a07be20>
DEBUG     botocore.hooks                            Event before-call.s3.HeadObject: calling handler <function inject_api_version_header_if_needed at 0x75202a07b010>
DEBUG     botocore.endpoint                         Making request for OperationModel(name=HeadObject) with params: {'url_path': '/raw/1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7/v1/BOTUVIC_v1.0_Product_Specification_UPDATED.md', 'query_string': {}, 'method': 'HEAD', 'headers': {'User-Agent': 'Boto3/1.35.85 md/Botocore#1.35.99 ua/2.0 os/linux#6.8.0-1048-gcp md/arch#x86_64 lang/python#3.10.12 md/pyimpl#CPython cfg/retry-mode#legacy Botocore/1.35.99'}, 'body': b'', 'auth_path': '/aiveilix/raw/1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7/v1/BOTUVIC_v1.0_Product_Specification_UPDATED.md', 'url': 'https://93d07d6cff38141aaf5eed882cda6725.r2.cloudflarestorage.com/aiveilix/raw/1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7/v1/BOTUVIC_v1.0_Product_Specification_UPDATED.md', 'context': {'client_region': 'auto', 'client_config': <botocore.config.Config object at 0x751f59e360b0>, 'has_streaming_input': False, 'auth_type': 'v4', 'unsigned_payload': None, 's3_redirect': {'redirected': False, 'bucket': 'aiveilix', 'params': {'Bucket': 'aiveilix', 'Key': 'raw/1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7/v1/BOTUVIC_v1.0_Product_Specification_UPDATED.md'}}, 'input_params': {'Bucket': 'aiveilix', 'Key': 'raw/1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7/v1/BOTUVIC_v1.0_Product_Specification_UPDATED.md'}, 'signing': {'region': 'auto', 'signing_name': 's3', 'disableDoubleEncoding': True}, 'endpoint_properties': {'authSchemes': [{'disableDoubleEncoding': True, 'name': 'sigv4', 'signingName': 's3', 'signingRegion': 'auto'}]}}}
DEBUG     botocore.hooks                            Event request-created.s3.HeadObject: calling handler <function signal_not_transferring at 0x751f59ff8ca0>
DEBUG     botocore.hooks                            Event request-created.s3.HeadObject: calling handler <bound method RequestSigner.handler of <botocore.signers.RequestSigner object at 0x751f59f9db40>>
DEBUG     botocore.hooks                            Event choose-signer.s3.HeadObject: calling handler <function set_operation_specific_signer at 0x75202a079630>
DEBUG     botocore.hooks                            Event before-sign.s3.HeadObject: calling handler <function remove_arn_from_signing_path at 0x75202a07b910>
DEBUG     botocore.hooks                            Event before-sign.s3.HeadObject: calling handler <bound method S3ExpressIdentityResolver.resolve_s3express_identity of <botocore.utils.S3ExpressIdentityResolver object at 0x751f59e81e70>>
DEBUG     botocore.auth                             Calculating signature using v4 auth.
DEBUG     botocore.auth                             CanonicalRequest:
HEAD
/aiveilix/raw/1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7/v1/BOTUVIC_v1.0_Product_Specification_UPDATED.md

host:93d07d6cff38141aaf5eed882cda6725.r2.cloudflarestorage.com
x-amz-content-sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
x-amz-date:20260406T021425Z

host;x-amz-content-sha256;x-amz-date
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
DEBUG     botocore.auth                             StringToSign:
AWS4-HMAC-SHA256
20260406T021425Z
20260406/auto/s3/aws4_request
d1d4f367e7aa9fdf44aa5af6c02c9800cca7f88c10ad9afbd607b2ce0e9db406
DEBUG     botocore.auth                             Signature:
b677a00acfa60f719c9ed350f18d042e8667515eb3cb39b6298d5bddd32f1888
DEBUG     botocore.hooks                            Event request-created.s3.HeadObject: calling handler <function signal_transferring at 0x751f59ff8d30>
DEBUG     botocore.hooks                            Event request-created.s3.HeadObject: calling handler <function add_retry_headers at 0x75202a07b760>
DEBUG     botocore.endpoint                         Sending http request: <AWSPreparedRequest stream_output=False, method=HEAD, url=https://93d07d6cff38141aaf5eed882cda6725.r2.cloudflarestorage.com/aiveilix/raw/1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7/v1/BOTUVIC_v1.0_Product_Specification_UPDATED.md, headers={'User-Agent': b'Boto3/1.35.85 md/Botocore#1.35.99 ua/2.0 os/linux#6.8.0-1048-gcp md/arch#x86_64 lang/python#3.10.12 md/pyimpl#CPython cfg/retry-mode#legacy Botocore/1.35.99', 'X-Amz-Date': b'20260406T021425Z', 'X-Amz-Content-SHA256': b'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', 'Authorization': b'AWS4-HMAC-SHA256 Credential=a14d95abb63a7791c665f6833e04b1ea/20260406/auto/s3/aws4_request, SignedHeaders=host;x-amz-content-sha256;x-amz-date, Signature=b677a00acfa60f719c9ed350f18d042e8667515eb3cb39b6298d5bddd32f1888', 'amz-sdk-invocation-id': b'1b936646-7728-49cd-a8c7-e060f136802f', 'amz-sdk-request': b'attempt=1'}>
DEBUG     botocore.httpsession                      Certificate path: /home/chaffanjutt/AIVEILIX/backend/.venv/lib/python3.10/site-packages/certifi/cacert.pem
DEBUG     urllib3.connectionpool                    https://93d07d6cff38141aaf5eed882cda6725.r2.cloudflarestorage.com:443 "HEAD /aiveilix/raw/1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7/v1/BOTUVIC_v1.0_Product_Specification_UPDATED.md HTTP/1.1" 200 0
DEBUG     botocore.hooks                            Event before-parse.s3.HeadObject: calling handler <function _handle_200_error at 0x75202a07bc70>
DEBUG     botocore.hooks                            Event before-parse.s3.HeadObject: calling handler <function handle_expires_header at 0x75202a07bac0>
DEBUG     botocore.parsers                          Response headers: {'Date': 'Mon, 06 Apr 2026 02:14:25 GMT', 'Content-Type': 'text/markdown', 'Content-Length': '70628', 'Connection': 'keep-alive', 'Accept-Ranges': 'bytes', 'ETag': '"17443a87e3d89f964da0151f468fae79"', 'Last-Modified': 'Mon, 06 Apr 2026 02:14:25 GMT', 'Vary': 'Accept-Encoding', 'Server': 'cloudflare', 'CF-RAY': '9e7d476bce533f22-NRT'}
DEBUG     botocore.parsers                          Response body:
b''
DEBUG     botocore.hooks                            Event needs-retry.s3.HeadObject: calling handler <function _update_status_code at 0x75202a07bd90>
DEBUG     botocore.hooks                            Event needs-retry.s3.HeadObject: calling handler <botocore.retryhandler.RetryHandler object at 0x751f59e81d50>
DEBUG     botocore.retryhandler                     No retry needed.
DEBUG     botocore.hooks                            Event needs-retry.s3.HeadObject: calling handler <bound method S3RegionRedirectorv2.redirect_from_error of <botocore.utils.S3RegionRedirectorv2 object at 0x751f59e81e10>>
DEBUG     s3transfer.futures                        Submitting task ImmediatelyWriteIOGetObjectTask(transfer_id=0, {'bucket': 'aiveilix', 'key': 'raw/1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7/v1/BOTUVIC_v1.0_Product_Specification_UPDATED.md', 'extra_args': {}}) to executor <s3transfer.futures.BoundedExecutor object at 0x751f59ee27a0> for transfer request: 0.
DEBUG     s3transfer.utils                          Acquiring 0
DEBUG     s3transfer.tasks                          ImmediatelyWriteIOGetObjectTask(transfer_id=0, {'bucket': 'aiveilix', 'key': 'raw/1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7/v1/BOTUVIC_v1.0_Product_Specification_UPDATED.md', 'extra_args': {}}) about to wait for the following futures []
DEBUG     s3transfer.tasks                          ImmediatelyWriteIOGetObjectTask(transfer_id=0, {'bucket': 'aiveilix', 'key': 'raw/1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7/v1/BOTUVIC_v1.0_Product_Specification_UPDATED.md', 'extra_args': {}}) done waiting for dependent futures
DEBUG     s3transfer.tasks                          Executing task ImmediatelyWriteIOGetObjectTask(transfer_id=0, {'bucket': 'aiveilix', 'key': 'raw/1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7/v1/BOTUVIC_v1.0_Product_Specification_UPDATED.md', 'extra_args': {}}) with kwargs {'client': <botocore.client.S3 object at 0x751f59f9d360>, 'bucket': 'aiveilix', 'key': 'raw/1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7/v1/BOTUVIC_v1.0_Product_Specification_UPDATED.md', 'fileobj': <_io.BytesIO object at 0x751f5c733330>, 'extra_args': {}, 'callbacks': [], 'max_attempts': 5, 'download_output_manager': <s3transfer.download.DownloadSeekableOutputManager object at 0x751f59ee1e40>, 'io_chunksize': 262144, 'bandwidth_limiter': None}
DEBUG     botocore.hooks                            Event before-parameter-build.s3.GetObject: calling handler <function sse_md5 at 0x75202a079a20>
DEBUG     botocore.hooks                            Event before-parameter-build.s3.GetObject: calling handler <function validate_bucket_name at 0x75202a079990>
DEBUG     botocore.hooks                            Event before-parameter-build.s3.GetObject: calling handler <function remove_bucket_from_url_paths_from_model at 0x75202a07b7f0>
DEBUG     botocore.hooks                            Event before-parameter-build.s3.GetObject: calling handler <bound method S3RegionRedirectorv2.annotate_request_context of <botocore.utils.S3RegionRedirectorv2 object at 0x751f59e81e10>>
DEBUG     s3transfer.utils                          Releasing acquire 0/None
DEBUG     botocore.hooks                            Event before-parameter-build.s3.GetObject: calling handler <bound method ClientCreator._inject_s3_input_parameters of <botocore.client.ClientCreator object at 0x751f5a967130>>
DEBUG     botocore.hooks                            Event before-parameter-build.s3.GetObject: calling handler <function generate_idempotent_uuid at 0x75202a0797e0>
DEBUG     botocore.hooks                            Event before-endpoint-resolution.s3: calling handler <function customize_endpoint_resolver_builtins at 0x75202a07b9a0>
DEBUG     botocore.hooks                            Event before-endpoint-resolution.s3: calling handler <bound method S3RegionRedirectorv2.redirect_from_cache of <botocore.utils.S3RegionRedirectorv2 object at 0x751f59e81e10>>
DEBUG     botocore.regions                          Calling endpoint provider with parameters: {'Bucket': 'aiveilix', 'Region': 'auto', 'UseFIPS': False, 'UseDualStack': False, 'Endpoint': 'https://93d07d6cff38141aaf5eed882cda6725.r2.cloudflarestorage.com', 'ForcePathStyle': True, 'Accelerate': False, 'UseGlobalEndpoint': False, 'Key': 'raw/1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7/v1/BOTUVIC_v1.0_Product_Specification_UPDATED.md', 'DisableMultiRegionAccessPoints': False, 'UseArnRegion': True}
DEBUG     botocore.regions                          Endpoint provider result: https://93d07d6cff38141aaf5eed882cda6725.r2.cloudflarestorage.com/aiveilix
DEBUG     botocore.regions                          Selecting from endpoint provider's list of auth schemes: "sigv4". User selected auth scheme is: "None"
DEBUG     botocore.regions                          Selected auth type "v4" as "v4" with signing context params: {'region': 'auto', 'signing_name': 's3', 'disableDoubleEncoding': True}
DEBUG     botocore.hooks                            Event before-call.s3.GetObject: calling handler <function add_expect_header at 0x75202a079cf0>
DEBUG     botocore.hooks                            Event before-call.s3.GetObject: calling handler <bound method S3ExpressIdentityResolver.apply_signing_cache_key of <botocore.utils.S3ExpressIdentityResolver object at 0x751f59e81e70>>
DEBUG     botocore.hooks                            Event before-call.s3.GetObject: calling handler <function add_recursion_detection_header at 0x75202a0793f0>
DEBUG     botocore.hooks                            Event before-call.s3.GetObject: calling handler <function add_query_compatibility_header at 0x75202a07be20>
DEBUG     botocore.hooks                            Event before-call.s3.GetObject: calling handler <function inject_api_version_header_if_needed at 0x75202a07b010>
DEBUG     botocore.endpoint                         Making request for OperationModel(name=GetObject) with params: {'url_path': '/raw/1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7/v1/BOTUVIC_v1.0_Product_Specification_UPDATED.md', 'query_string': {}, 'method': 'GET', 'headers': {'User-Agent': 'Boto3/1.35.85 md/Botocore#1.35.99 ua/2.0 os/linux#6.8.0-1048-gcp md/arch#x86_64 lang/python#3.10.12 md/pyimpl#CPython cfg/retry-mode#legacy Botocore/1.35.99'}, 'body': b'', 'auth_path': '/aiveilix/raw/1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7/v1/BOTUVIC_v1.0_Product_Specification_UPDATED.md', 'url': 'https://93d07d6cff38141aaf5eed882cda6725.r2.cloudflarestorage.com/aiveilix/raw/1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7/v1/BOTUVIC_v1.0_Product_Specification_UPDATED.md', 'context': {'client_region': 'auto', 'client_config': <botocore.config.Config object at 0x751f59e360b0>, 'has_streaming_input': False, 'auth_type': 'v4', 'unsigned_payload': None, 's3_redirect': {'redirected': False, 'bucket': 'aiveilix', 'params': {'Bucket': 'aiveilix', 'Key': 'raw/1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7/v1/BOTUVIC_v1.0_Product_Specification_UPDATED.md'}}, 'input_params': {'Bucket': 'aiveilix', 'Key': 'raw/1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7/v1/BOTUVIC_v1.0_Product_Specification_UPDATED.md'}, 'signing': {'region': 'auto', 'signing_name': 's3', 'disableDoubleEncoding': True}, 'endpoint_properties': {'authSchemes': [{'disableDoubleEncoding': True, 'name': 'sigv4', 'signingName': 's3', 'signingRegion': 'auto'}]}}}
DEBUG     botocore.hooks                            Event request-created.s3.GetObject: calling handler <function signal_not_transferring at 0x751f59ff8ca0>
DEBUG     botocore.hooks                            Event request-created.s3.GetObject: calling handler <bound method RequestSigner.handler of <botocore.signers.RequestSigner object at 0x751f59f9db40>>
DEBUG     botocore.hooks                            Event choose-signer.s3.GetObject: calling handler <function set_operation_specific_signer at 0x75202a079630>
DEBUG     botocore.hooks                            Event before-sign.s3.GetObject: calling handler <function remove_arn_from_signing_path at 0x75202a07b910>
DEBUG     botocore.hooks                            Event before-sign.s3.GetObject: calling handler <bound method S3ExpressIdentityResolver.resolve_s3express_identity of <botocore.utils.S3ExpressIdentityResolver object at 0x751f59e81e70>>
DEBUG     botocore.auth                             Calculating signature using v4 auth.
DEBUG     botocore.auth                             CanonicalRequest:
GET
/aiveilix/raw/1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7/v1/BOTUVIC_v1.0_Product_Specification_UPDATED.md

host:93d07d6cff38141aaf5eed882cda6725.r2.cloudflarestorage.com
x-amz-content-sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
x-amz-date:20260406T021426Z

host;x-amz-content-sha256;x-amz-date
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
DEBUG     botocore.auth                             StringToSign:
AWS4-HMAC-SHA256
20260406T021426Z
20260406/auto/s3/aws4_request
3f533dfad5620d22bd73f2c7ac870079e7c9f20725e6994b7852ebf4adc41d8c
DEBUG     botocore.auth                             Signature:
3053ff2d13188bca6a060e4d0c73bbaa5c122d9afeb215965df0bbb4523e8acc
DEBUG     botocore.hooks                            Event request-created.s3.GetObject: calling handler <function signal_transferring at 0x751f59ff8d30>
DEBUG     botocore.hooks                            Event request-created.s3.GetObject: calling handler <function add_retry_headers at 0x75202a07b760>
DEBUG     botocore.endpoint                         Sending http request: <AWSPreparedRequest stream_output=True, method=GET, url=https://93d07d6cff38141aaf5eed882cda6725.r2.cloudflarestorage.com/aiveilix/raw/1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7/v1/BOTUVIC_v1.0_Product_Specification_UPDATED.md, headers={'User-Agent': b'Boto3/1.35.85 md/Botocore#1.35.99 ua/2.0 os/linux#6.8.0-1048-gcp md/arch#x86_64 lang/python#3.10.12 md/pyimpl#CPython cfg/retry-mode#legacy Botocore/1.35.99', 'X-Amz-Date': b'20260406T021426Z', 'X-Amz-Content-SHA256': b'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', 'Authorization': b'AWS4-HMAC-SHA256 Credential=a14d95abb63a7791c665f6833e04b1ea/20260406/auto/s3/aws4_request, SignedHeaders=host;x-amz-content-sha256;x-amz-date, Signature=3053ff2d13188bca6a060e4d0c73bbaa5c122d9afeb215965df0bbb4523e8acc', 'amz-sdk-invocation-id': b'42c8016d-3018-4cd5-b2e4-206eb4aeedfe', 'amz-sdk-request': b'attempt=1'}>
DEBUG     botocore.httpsession                      Certificate path: /home/chaffanjutt/AIVEILIX/backend/.venv/lib/python3.10/site-packages/certifi/cacert.pem
DEBUG     urllib3.connectionpool                    https://93d07d6cff38141aaf5eed882cda6725.r2.cloudflarestorage.com:443 "GET /aiveilix/raw/1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7/v1/BOTUVIC_v1.0_Product_Specification_UPDATED.md HTTP/1.1" 200 70628
DEBUG     botocore.hooks                            Event before-parse.s3.GetObject: calling handler <function _handle_200_error at 0x75202a07bc70>
DEBUG     botocore.hooks                            Event before-parse.s3.GetObject: calling handler <function handle_expires_header at 0x75202a07bac0>
DEBUG     botocore.parsers                          Response headers: {'Date': 'Mon, 06 Apr 2026 02:14:26 GMT', 'Content-Type': 'text/markdown', 'Content-Length': '70628', 'Connection': 'keep-alive', 'Accept-Ranges': 'bytes', 'ETag': '"17443a87e3d89f964da0151f468fae79"', 'Last-Modified': 'Mon, 06 Apr 2026 02:14:25 GMT', 'Vary': 'Accept-Encoding', 'Server': 'cloudflare', 'CF-RAY': '9e7d476c981a3f22-NRT'}
DEBUG     botocore.parsers                          Response body:
<botocore.response.StreamingBody object at 0x751f58d3f010>
DEBUG     botocore.hooks                            Event needs-retry.s3.GetObject: calling handler <function _update_status_code at 0x75202a07bd90>
DEBUG     botocore.hooks                            Event needs-retry.s3.GetObject: calling handler <botocore.retryhandler.RetryHandler object at 0x751f59e81d50>
DEBUG     botocore.retryhandler                     No retry needed.
DEBUG     botocore.hooks                            Event needs-retry.s3.GetObject: calling handler <bound method S3RegionRedirectorv2.redirect_from_error of <botocore.utils.S3RegionRedirectorv2 object at 0x751f59e81e10>>
DEBUG     s3transfer.tasks                          IOWriteTask(transfer_id=0, {'offset': 0}) about to wait for the following futures []
DEBUG     s3transfer.tasks                          IOWriteTask(transfer_id=0, {'offset': 0}) done waiting for dependent futures
DEBUG     s3transfer.tasks                          Executing task IOWriteTask(transfer_id=0, {'offset': 0}) with kwargs {'fileobj': <_io.BytesIO object at 0x751f5c733330>, 'offset': 0}
DEBUG     s3transfer.tasks                          CompleteDownloadNOOPTask(transfer_id=0, {}) about to wait for the following futures []
DEBUG     s3transfer.tasks                          CompleteDownloadNOOPTask(transfer_id=0, {}) done waiting for dependent futures
DEBUG     s3transfer.tasks                          Executing task CompleteDownloadNOOPTask(transfer_id=0, {}) with kwargs {}
DEBUG     s3transfer.utils                          Releasing acquire 0/None
2026-04-06 02:14:26,178 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:14:26,179 INFO sqlalchemy.engine.Engine INSERT INTO investigation_events (id, file_id, event, status, metadata) VALUES ($1::UUID, $2::UUID, $3::VARCHAR, $4::event_status, $5::JSONB) RETURNING investigation_events.created_at
INFO      sqlalchemy.engine.Engine                  INSERT INTO investigation_events (id, file_id, event, status, metadata) VALUES ($1::UUID, $2::UUID, $3::VARCHAR, $4::event_status, $5::JSONB) RETURNING investigation_events.created_at
2026-04-06 02:14:26,179 INFO sqlalchemy.engine.Engine [cached since 0.4741s ago] (UUID('2d68d52f-5a87-4cc1-9df2-68a33b29e40a'), UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'), 'download_completed', 'completed', '{"trace_run_id": "d313c038-8766-431e-848d-542087af1456", "trigger_source": "upload", "stage": "download", "sequence": 5, "recorded_at": "2026-04-06T02:14:26.175370+00:00", "size": 70628, "duration_ms": 335}')
INFO      sqlalchemy.engine.Engine                  [cached since 0.4741s ago] (UUID('2d68d52f-5a87-4cc1-9df2-68a33b29e40a'), UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'), 'download_completed', 'completed', '{"trace_run_id": "d313c038-8766-431e-848d-542087af1456", "trigger_source": "upload", "stage": "download", "sequence": 5, "recorded_at": "2026-04-06T02:14:26.175370+00:00", "size": 70628, "duration_ms": 335}')
2026-04-06 02:14:26,182 INFO sqlalchemy.engine.Engine COMMIT
INFO      sqlalchemy.engine.Engine                  COMMIT
INFO      app.services.pipeline.orchestrator        pipeline_trace file=1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7 trace=d313c038-8766-431e-848d-542087af1456 event=download_completed stage=download status=completed metadata={'trace_run_id': 'd313c038-8766-431e-848d-542087af1456', 'trigger_source': 'upload', 'stage': 'download', 'sequence': 5, 'recorded_at': '2026-04-06T02:14:26.175370+00:00', 'size': 70628, 'duration_ms': 335}
2026-04-06 02:14:26,187 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:14:26,188 INFO sqlalchemy.engine.Engine INSERT INTO investigation_events (id, file_id, event, status, metadata) VALUES ($1::UUID, $2::UUID, $3::VARCHAR, $4::event_status, $5::JSONB) RETURNING investigation_events.created_at
INFO      sqlalchemy.engine.Engine                  INSERT INTO investigation_events (id, file_id, event, status, metadata) VALUES ($1::UUID, $2::UUID, $3::VARCHAR, $4::event_status, $5::JSONB) RETURNING investigation_events.created_at
2026-04-06 02:14:26,188 INFO sqlalchemy.engine.Engine [cached since 0.4835s ago] (UUID('e0870376-2558-4aa3-a3e9-b0714409f464'), UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'), 'docling_started', 'started', '{"trace_run_id": "d313c038-8766-431e-848d-542087af1456", "trigger_source": "upload", "stage": "docling", "sequence": 6, "recorded_at": "2026-04-06T02:14:26.185431+00:00"}')
INFO      sqlalchemy.engine.Engine                  [cached since 0.4835s ago] (UUID('e0870376-2558-4aa3-a3e9-b0714409f464'), UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'), 'docling_started', 'started', '{"trace_run_id": "d313c038-8766-431e-848d-542087af1456", "trigger_source": "upload", "stage": "docling", "sequence": 6, "recorded_at": "2026-04-06T02:14:26.185431+00:00"}')
2026-04-06 02:14:26,191 INFO sqlalchemy.engine.Engine COMMIT
INFO      sqlalchemy.engine.Engine                  COMMIT
INFO      app.services.pipeline.orchestrator        pipeline_trace file=1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7 trace=d313c038-8766-431e-848d-542087af1456 event=docling_started stage=docling status=started metadata={'trace_run_id': 'd313c038-8766-431e-848d-542087af1456', 'trigger_source': 'upload', 'stage': 'docling', 'sequence': 6, 'recorded_at': '2026-04-06T02:14:26.185431+00:00'}
2026-04-06 02:14:28,806 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:14:28,807 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:14:28,808 INFO sqlalchemy.engine.Engine [cached since 17.6s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 17.6s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:14:28,813 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
2026-04-06 02:14:28,813 INFO sqlalchemy.engine.Engine [cached since 17.59s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 17.59s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:14:28,817 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:14:32,273 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:14:32,274 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:14:32,275 INFO sqlalchemy.engine.Engine [cached since 21.07s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 21.07s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:14:32,278 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
2026-04-06 02:14:32,279 INFO sqlalchemy.engine.Engine [cached since 21.05s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 21.05s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:14:32,285 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:14:36,781 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:14:36,782 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:14:36,783 INFO sqlalchemy.engine.Engine [cached since 25.58s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 25.58s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:14:36,787 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
2026-04-06 02:14:36,787 INFO sqlalchemy.engine.Engine [cached since 25.56s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 25.56s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:14:36,799 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:14:40,588 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:14:40,589 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:14:40,590 INFO sqlalchemy.engine.Engine [cached since 29.39s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 29.39s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:14:40,596 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
2026-04-06 02:14:40,596 INFO sqlalchemy.engine.Engine [cached since 29.37s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 29.37s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:14:40,599 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
INFO      app.services.processing.docling_service   Docling input format resolved to md for BOTUVIC_v1.0_Product_Specification_UPDATED.md
INFO      app.services.processing.docling_service   Docling extracted 1096 blocks, 1 pages, 0 page images from BOTUVIC_v1.0_Product_Specification_UPDATED.md
2026-04-06 02:14:43,493 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:14:43,494 INFO sqlalchemy.engine.Engine INSERT INTO investigation_events (id, file_id, event, status, metadata) VALUES ($1::UUID, $2::UUID, $3::VARCHAR, $4::event_status, $5::JSONB) RETURNING investigation_events.created_at
INFO      sqlalchemy.engine.Engine                  INSERT INTO investigation_events (id, file_id, event, status, metadata) VALUES ($1::UUID, $2::UUID, $3::VARCHAR, $4::event_status, $5::JSONB) RETURNING investigation_events.created_at
2026-04-06 02:14:43,495 INFO sqlalchemy.engine.Engine [cached since 17.79s ago] (UUID('aca5cbdc-e39d-4e11-915f-5cf47b2b4828'), UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'), 'docling_completed', 'completed', '{"trace_run_id": "d313c038-8766-431e-848d-542087af1456", "trigger_source": "upload", "stage": "docling", "sequence": 7, "recorded_at": "2026-04-06T02:14:43.491444+00:00", "blocks": 1096, "pages": 1, "duration_ms": 17305}')
INFO      sqlalchemy.engine.Engine                  [cached since 17.79s ago] (UUID('aca5cbdc-e39d-4e11-915f-5cf47b2b4828'), UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'), 'docling_completed', 'completed', '{"trace_run_id": "d313c038-8766-431e-848d-542087af1456", "trigger_source": "upload", "stage": "docling", "sequence": 7, "recorded_at": "2026-04-06T02:14:43.491444+00:00", "blocks": 1096, "pages": 1, "duration_ms": 17305}')
2026-04-06 02:14:43,497 INFO sqlalchemy.engine.Engine COMMIT
INFO      sqlalchemy.engine.Engine                  COMMIT
INFO      app.services.pipeline.orchestrator        pipeline_trace file=1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7 trace=d313c038-8766-431e-848d-542087af1456 event=docling_completed stage=docling status=completed metadata={'trace_run_id': 'd313c038-8766-431e-848d-542087af1456', 'trigger_source': 'upload', 'stage': 'docling', 'sequence': 7, 'recorded_at': '2026-04-06T02:14:43.491444+00:00', 'blocks': 1096, 'pages': 1, 'duration_ms': 17305}
2026-04-06 02:14:43,502 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:14:43,503 INFO sqlalchemy.engine.Engine INSERT INTO investigation_events (id, file_id, event, status, metadata) VALUES ($1::UUID, $2::UUID, $3::VARCHAR, $4::event_status, $5::JSONB) RETURNING investigation_events.created_at
INFO      sqlalchemy.engine.Engine                  INSERT INTO investigation_events (id, file_id, event, status, metadata) VALUES ($1::UUID, $2::UUID, $3::VARCHAR, $4::event_status, $5::JSONB) RETURNING investigation_events.created_at
2026-04-06 02:14:43,504 INFO sqlalchemy.engine.Engine [cached since 17.8s ago] (UUID('b66602c1-dc3d-4df0-b04d-28640641c86f'), UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'), 'gemini_skipped', 'completed', '{"trace_run_id": "d313c038-8766-431e-848d-542087af1456", "trigger_source": "upload", "stage": "gemini", "sequence": 8, "recorded_at": "2026-04-06T02:14:43.501098+00:00", "reason": "no_image_blocks"}')
INFO      sqlalchemy.engine.Engine                  [cached since 17.8s ago] (UUID('b66602c1-dc3d-4df0-b04d-28640641c86f'), UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'), 'gemini_skipped', 'completed', '{"trace_run_id": "d313c038-8766-431e-848d-542087af1456", "trigger_source": "upload", "stage": "gemini", "sequence": 8, "recorded_at": "2026-04-06T02:14:43.501098+00:00", "reason": "no_image_blocks"}')
2026-04-06 02:14:43,507 INFO sqlalchemy.engine.Engine COMMIT
INFO      sqlalchemy.engine.Engine                  COMMIT
INFO      app.services.pipeline.orchestrator        pipeline_trace file=1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7 trace=d313c038-8766-431e-848d-542087af1456 event=gemini_skipped stage=gemini status=completed metadata={'trace_run_id': 'd313c038-8766-431e-848d-542087af1456', 'trigger_source': 'upload', 'stage': 'gemini', 'sequence': 8, 'recorded_at': '2026-04-06T02:14:43.501098+00:00', 'reason': 'no_image_blocks'}
2026-04-06 02:14:43,512 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:14:43,513 INFO sqlalchemy.engine.Engine INSERT INTO investigation_events (id, file_id, event, status, metadata) VALUES ($1::UUID, $2::UUID, $3::VARCHAR, $4::event_status, $5::JSONB) RETURNING investigation_events.created_at
INFO      sqlalchemy.engine.Engine                  INSERT INTO investigation_events (id, file_id, event, status, metadata) VALUES ($1::UUID, $2::UUID, $3::VARCHAR, $4::event_status, $5::JSONB) RETURNING investigation_events.created_at
2026-04-06 02:14:43,514 INFO sqlalchemy.engine.Engine [cached since 17.81s ago] (UUID('d9021697-4693-4303-ad14-229f50aafaf8'), UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'), 'gemini_page_ocr_skipped', 'completed', '{"trace_run_id": "d313c038-8766-431e-848d-542087af1456", "trigger_source": "upload", "stage": "gemini_page_ocr", "sequence": 9, "recorded_at": "2026-04-06T02:14:43.510709+00:00", "reason": "no_garbled_pages"}')
INFO      sqlalchemy.engine.Engine                  [cached since 17.81s ago] (UUID('d9021697-4693-4303-ad14-229f50aafaf8'), UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'), 'gemini_page_ocr_skipped', 'completed', '{"trace_run_id": "d313c038-8766-431e-848d-542087af1456", "trigger_source": "upload", "stage": "gemini_page_ocr", "sequence": 9, "recorded_at": "2026-04-06T02:14:43.510709+00:00", "reason": "no_garbled_pages"}')
2026-04-06 02:14:43,516 INFO sqlalchemy.engine.Engine COMMIT
INFO      sqlalchemy.engine.Engine                  COMMIT
INFO      app.services.pipeline.orchestrator        pipeline_trace file=1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7 trace=d313c038-8766-431e-848d-542087af1456 event=gemini_page_ocr_skipped stage=gemini_page_ocr status=completed metadata={'trace_run_id': 'd313c038-8766-431e-848d-542087af1456', 'trigger_source': 'upload', 'stage': 'gemini_page_ocr', 'sequence': 9, 'recorded_at': '2026-04-06T02:14:43.510709+00:00', 'reason': 'no_garbled_pages'}
2026-04-06 02:14:43,522 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:14:43,523 INFO sqlalchemy.engine.Engine INSERT INTO investigation_events (id, file_id, event, status, metadata) VALUES ($1::UUID, $2::UUID, $3::VARCHAR, $4::event_status, $5::JSONB) RETURNING investigation_events.created_at
INFO      sqlalchemy.engine.Engine                  INSERT INTO investigation_events (id, file_id, event, status, metadata) VALUES ($1::UUID, $2::UUID, $3::VARCHAR, $4::event_status, $5::JSONB) RETURNING investigation_events.created_at
2026-04-06 02:14:43,523 INFO sqlalchemy.engine.Engine [cached since 17.82s ago] (UUID('a30cbf0b-50aa-4729-944a-930bdd67bc25'), UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'), 'layout_build_started', 'started', '{"trace_run_id": "d313c038-8766-431e-848d-542087af1456", "trigger_source": "upload", "stage": "layout_build", "sequence": 10, "recorded_at": "2026-04-06T02:14:43.518989+00:00"}')
INFO      sqlalchemy.engine.Engine                  [cached since 17.82s ago] (UUID('a30cbf0b-50aa-4729-944a-930bdd67bc25'), UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'), 'layout_build_started', 'started', '{"trace_run_id": "d313c038-8766-431e-848d-542087af1456", "trigger_source": "upload", "stage": "layout_build", "sequence": 10, "recorded_at": "2026-04-06T02:14:43.518989+00:00"}')
2026-04-06 02:14:43,525 INFO sqlalchemy.engine.Engine COMMIT
INFO      sqlalchemy.engine.Engine                  COMMIT
INFO      app.services.pipeline.orchestrator        pipeline_trace file=1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7 trace=d313c038-8766-431e-848d-542087af1456 event=layout_build_started stage=layout_build status=started metadata={'trace_run_id': 'd313c038-8766-431e-848d-542087af1456', 'trigger_source': 'upload', 'stage': 'layout_build', 'sequence': 10, 'recorded_at': '2026-04-06T02:14:43.518989+00:00'}
INFO      app.services.processing.layout_builder    Layout built for file 1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7: 1 pages, 1096 total blocks
2026-04-06 02:14:43,531 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:14:43,532 INFO sqlalchemy.engine.Engine INSERT INTO investigation_events (id, file_id, event, status, metadata) VALUES ($1::UUID, $2::UUID, $3::VARCHAR, $4::event_status, $5::JSONB) RETURNING investigation_events.created_at
INFO      sqlalchemy.engine.Engine                  INSERT INTO investigation_events (id, file_id, event, status, metadata) VALUES ($1::UUID, $2::UUID, $3::VARCHAR, $4::event_status, $5::JSONB) RETURNING investigation_events.created_at
2026-04-06 02:14:43,533 INFO sqlalchemy.engine.Engine [cached since 17.83s ago] (UUID('f5485117-e620-4d3b-822d-37a1e4230723'), UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'), 'layout_build_completed', 'completed', '{"trace_run_id": "d313c038-8766-431e-848d-542087af1456", "trigger_source": "upload", "stage": "layout_build", "sequence": 11, "recorded_at": "2026-04-06T02:14:43.530134+00:00", "pages": 1, "duration_ms": 11}')
INFO      sqlalchemy.engine.Engine                  [cached since 17.83s ago] (UUID('f5485117-e620-4d3b-822d-37a1e4230723'), UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'), 'layout_build_completed', 'completed', '{"trace_run_id": "d313c038-8766-431e-848d-542087af1456", "trigger_source": "upload", "stage": "layout_build", "sequence": 11, "recorded_at": "2026-04-06T02:14:43.530134+00:00", "pages": 1, "duration_ms": 11}')
2026-04-06 02:14:43,534 INFO sqlalchemy.engine.Engine COMMIT
INFO      sqlalchemy.engine.Engine                  COMMIT
INFO      app.services.pipeline.orchestrator        pipeline_trace file=1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7 trace=d313c038-8766-431e-848d-542087af1456 event=layout_build_completed stage=layout_build status=completed metadata={'trace_run_id': 'd313c038-8766-431e-848d-542087af1456', 'trigger_source': 'upload', 'stage': 'layout_build', 'sequence': 11, 'recorded_at': '2026-04-06T02:14:43.530134+00:00', 'pages': 1, 'duration_ms': 11}
2026-04-06 02:14:43,540 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:14:43,541 INFO sqlalchemy.engine.Engine INSERT INTO investigation_events (id, file_id, event, status, metadata) VALUES ($1::UUID, $2::UUID, $3::VARCHAR, $4::event_status, $5::JSONB) RETURNING investigation_events.created_at
INFO      sqlalchemy.engine.Engine                  INSERT INTO investigation_events (id, file_id, event, status, metadata) VALUES ($1::UUID, $2::UUID, $3::VARCHAR, $4::event_status, $5::JSONB) RETURNING investigation_events.created_at
2026-04-06 02:14:43,541 INFO sqlalchemy.engine.Engine [cached since 17.84s ago] (UUID('52cb6829-8d9f-49af-9ee7-cdaa7935d2ab'), UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'), 'file_summary_started', 'started', '{"trace_run_id": "d313c038-8766-431e-848d-542087af1456", "trigger_source": "upload", "stage": "file_summary", "sequence": 12, "recorded_at": "2026-04-06T02:14:43.538729+00:00"}')
INFO      sqlalchemy.engine.Engine                  [cached since 17.84s ago] (UUID('52cb6829-8d9f-49af-9ee7-cdaa7935d2ab'), UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'), 'file_summary_started', 'started', '{"trace_run_id": "d313c038-8766-431e-848d-542087af1456", "trigger_source": "upload", "stage": "file_summary", "sequence": 12, "recorded_at": "2026-04-06T02:14:43.538729+00:00"}')
2026-04-06 02:14:43,543 INFO sqlalchemy.engine.Engine COMMIT
INFO      sqlalchemy.engine.Engine                  COMMIT
INFO      app.services.pipeline.orchestrator        pipeline_trace file=1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7 trace=d313c038-8766-431e-848d-542087af1456 event=file_summary_started stage=file_summary status=started metadata={'trace_run_id': 'd313c038-8766-431e-848d-542087af1456', 'trigger_source': 'upload', 'stage': 'file_summary', 'sequence': 12, 'recorded_at': '2026-04-06T02:14:43.538729+00:00'}
2026-04-06 02:14:43,732 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:14:43,733 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:14:43,733 INFO sqlalchemy.engine.Engine [cached since 32.53s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 32.53s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:14:43,736 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
2026-04-06 02:14:43,737 INFO sqlalchemy.engine.Engine [cached since 32.51s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 32.51s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:14:43,739 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:14:46,767 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:14:46,769 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:14:46,769 INFO sqlalchemy.engine.Engine [cached since 35.57s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 35.57s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:14:46,772 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
2026-04-06 02:14:46,773 INFO sqlalchemy.engine.Engine [cached since 35.55s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 35.55s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:14:46,775 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:14:49,808 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:14:49,809 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:14:49,810 INFO sqlalchemy.engine.Engine [cached since 38.61s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 38.61s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:14:49,814 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
2026-04-06 02:14:49,815 INFO sqlalchemy.engine.Engine [cached since 38.59s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 38.59s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:14:49,818 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:14:50,726 INFO sqlalchemy.engine.Engine DELETE FROM summaries WHERE summaries.file_id = $1::UUID
INFO      sqlalchemy.engine.Engine                  DELETE FROM summaries WHERE summaries.file_id = $1::UUID
2026-04-06 02:14:50,726 INFO sqlalchemy.engine.Engine [generated in 0.00069s] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
INFO      sqlalchemy.engine.Engine                  [generated in 0.00069s] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
2026-04-06 02:14:50,731 INFO sqlalchemy.engine.Engine INSERT INTO summaries (id, file_id, bucket_id, content) VALUES ($1::UUID, $2::UUID, $3::UUID, $4::VARCHAR) RETURNING summaries.created_at
INFO      sqlalchemy.engine.Engine                  INSERT INTO summaries (id, file_id, bucket_id, content) VALUES ($1::UUID, $2::UUID, $3::UUID, $4::VARCHAR) RETURNING summaries.created_at
2026-04-06 02:14:50,732 INFO sqlalchemy.engine.Engine [generated in 0.00062s] (UUID('f5589e99-0eff-4f5a-bb3f-5529383bcff3'), UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'), None, 'Title: BOTUVIC v1.0 Product Specification\nDocument Type: Product Specification\n\nOverview:\nBotuvic is a desktop application featuring a self-learn ... (1632 characters truncated) ... rning mechanism for the Botuvic agent?\n- Which user segments are targeted by Botuvic?\n- What is the projected timeline for the MVP of Botuvic v1.0?')
INFO      sqlalchemy.engine.Engine                  [generated in 0.00062s] (UUID('f5589e99-0eff-4f5a-bb3f-5529383bcff3'), UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'), None, 'Title: BOTUVIC v1.0 Product Specification\nDocument Type: Product Specification\n\nOverview:\nBotuvic is a desktop application featuring a self-learn ... (1632 characters truncated) ... rning mechanism for the Botuvic agent?\n- Which user segments are targeted by Botuvic?\n- What is the projected timeline for the MVP of Botuvic v1.0?')
2026-04-06 02:14:50,738 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:14:50,739 INFO sqlalchemy.engine.Engine INSERT INTO investigation_events (id, file_id, event, status, metadata) VALUES ($1::UUID, $2::UUID, $3::VARCHAR, $4::event_status, $5::JSONB) RETURNING investigation_events.created_at
INFO      sqlalchemy.engine.Engine                  INSERT INTO investigation_events (id, file_id, event, status, metadata) VALUES ($1::UUID, $2::UUID, $3::VARCHAR, $4::event_status, $5::JSONB) RETURNING investigation_events.created_at
2026-04-06 02:14:50,739 INFO sqlalchemy.engine.Engine [cached since 25.03s ago] (UUID('959b6c81-563d-4666-861a-139492698f9f'), UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'), 'file_summary_completed', 'completed', '{"trace_run_id": "d313c038-8766-431e-848d-542087af1456", "trigger_source": "upload", "stage": "file_summary", "sequence": 13, "recorded_at": "2026-04-06T02:14:50.736154+00:00", "used_fallback": false, "error": null, "chars": 1908}')
INFO      sqlalchemy.engine.Engine                  [cached since 25.03s ago] (UUID('959b6c81-563d-4666-861a-139492698f9f'), UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'), 'file_summary_completed', 'completed', '{"trace_run_id": "d313c038-8766-431e-848d-542087af1456", "trigger_source": "upload", "stage": "file_summary", "sequence": 13, "recorded_at": "2026-04-06T02:14:50.736154+00:00", "used_fallback": false, "error": null, "chars": 1908}')
2026-04-06 02:14:50,741 INFO sqlalchemy.engine.Engine COMMIT
INFO      sqlalchemy.engine.Engine                  COMMIT
INFO      app.services.pipeline.orchestrator        pipeline_trace file=1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7 trace=d313c038-8766-431e-848d-542087af1456 event=file_summary_completed stage=file_summary status=completed metadata={'trace_run_id': 'd313c038-8766-431e-848d-542087af1456', 'trigger_source': 'upload', 'stage': 'file_summary', 'sequence': 13, 'recorded_at': '2026-04-06T02:14:50.736154+00:00', 'used_fallback': False, 'error': None, 'chars': 1908}
2026-04-06 02:14:50,747 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:14:50,748 INFO sqlalchemy.engine.Engine INSERT INTO investigation_events (id, file_id, event, status, metadata) VALUES ($1::UUID, $2::UUID, $3::VARCHAR, $4::event_status, $5::JSONB) RETURNING investigation_events.created_at
INFO      sqlalchemy.engine.Engine                  INSERT INTO investigation_events (id, file_id, event, status, metadata) VALUES ($1::UUID, $2::UUID, $3::VARCHAR, $4::event_status, $5::JSONB) RETURNING investigation_events.created_at
2026-04-06 02:14:50,748 INFO sqlalchemy.engine.Engine [cached since 25.04s ago] (UUID('27b1c4a2-3b61-4282-b5ed-b76800dd44cf'), UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'), 'layout_upload_started', 'started', '{"trace_run_id": "d313c038-8766-431e-848d-542087af1456", "trigger_source": "upload", "stage": "layout_upload", "sequence": 14, "recorded_at": "2026-04-06T02:14:50.745009+00:00"}')
INFO      sqlalchemy.engine.Engine                  [cached since 25.04s ago] (UUID('27b1c4a2-3b61-4282-b5ed-b76800dd44cf'), UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'), 'layout_upload_started', 'started', '{"trace_run_id": "d313c038-8766-431e-848d-542087af1456", "trigger_source": "upload", "stage": "layout_upload", "sequence": 14, "recorded_at": "2026-04-06T02:14:50.745009+00:00"}')
2026-04-06 02:14:50,750 INFO sqlalchemy.engine.Engine COMMIT
INFO      sqlalchemy.engine.Engine                  COMMIT
INFO      app.services.pipeline.orchestrator        pipeline_trace file=1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7 trace=d313c038-8766-431e-848d-542087af1456 event=layout_upload_started stage=layout_upload status=started metadata={'trace_run_id': 'd313c038-8766-431e-848d-542087af1456', 'trigger_source': 'upload', 'stage': 'layout_upload', 'sequence': 14, 'recorded_at': '2026-04-06T02:14:50.745009+00:00'}
DEBUG     boto3.s3.transfer                         Opting out of CRT Transfer Manager. Preferred client: auto, CRT available: False, Instance Optimized: False.
DEBUG     boto3.s3.transfer                         Using default client. pid: 18943, thread: 128781249298432
DEBUG     s3transfer.utils                          Acquiring 0
DEBUG     s3transfer.tasks                          UploadSubmissionTask(transfer_id=0, {'transfer_future': <s3transfer.futures.TransferFuture object at 0x751f37ac26b0>}) about to wait for the following futures []
DEBUG     s3transfer.tasks                          UploadSubmissionTask(transfer_id=0, {'transfer_future': <s3transfer.futures.TransferFuture object at 0x751f37ac26b0>}) done waiting for dependent futures
DEBUG     s3transfer.tasks                          Executing task UploadSubmissionTask(transfer_id=0, {'transfer_future': <s3transfer.futures.TransferFuture object at 0x751f37ac26b0>}) with kwargs {'client': <botocore.client.S3 object at 0x751f59f9d360>, 'config': <boto3.s3.transfer.TransferConfig object at 0x751f37ac0430>, 'osutil': <s3transfer.utils.OSUtils object at 0x751f37ac18a0>, 'request_executor': <s3transfer.futures.BoundedExecutor object at 0x751f37ac1de0>, 'transfer_future': <s3transfer.futures.TransferFuture object at 0x751f37ac26b0>}
DEBUG     s3transfer.futures                        Submitting task PutObjectTask(transfer_id=0, {'bucket': 'aiveilix', 'key': 'layouts/1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7/layout.json', 'extra_args': {'ContentType': 'application/json'}}) to executor <s3transfer.futures.BoundedExecutor object at 0x751f37ac1de0> for transfer request: 0.
DEBUG     s3transfer.utils                          Acquiring 0
DEBUG     s3transfer.tasks                          PutObjectTask(transfer_id=0, {'bucket': 'aiveilix', 'key': 'layouts/1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7/layout.json', 'extra_args': {'ContentType': 'application/json'}}) about to wait for the following futures []
DEBUG     s3transfer.utils                          Releasing acquire 0/None
DEBUG     s3transfer.tasks                          PutObjectTask(transfer_id=0, {'bucket': 'aiveilix', 'key': 'layouts/1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7/layout.json', 'extra_args': {'ContentType': 'application/json'}}) done waiting for dependent futures
DEBUG     s3transfer.tasks                          Executing task PutObjectTask(transfer_id=0, {'bucket': 'aiveilix', 'key': 'layouts/1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7/layout.json', 'extra_args': {'ContentType': 'application/json'}}) with kwargs {'client': <botocore.client.S3 object at 0x751f59f9d360>, 'fileobj': <s3transfer.utils.ReadFileChunk object at 0x751f37ac2ad0>, 'bucket': 'aiveilix', 'key': 'layouts/1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7/layout.json', 'extra_args': {'ContentType': 'application/json'}}
DEBUG     botocore.hooks                            Event before-parameter-build.s3.PutObject: calling handler <function validate_ascii_metadata at 0x75202a07a5f0>
DEBUG     botocore.hooks                            Event before-parameter-build.s3.PutObject: calling handler <function sse_md5 at 0x75202a079a20>
DEBUG     botocore.hooks                            Event before-parameter-build.s3.PutObject: calling handler <function convert_body_to_file_like_object at 0x75202a07aef0>
DEBUG     botocore.hooks                            Event before-parameter-build.s3.PutObject: calling handler <function validate_bucket_name at 0x75202a079990>
DEBUG     botocore.hooks                            Event before-parameter-build.s3.PutObject: calling handler <function remove_bucket_from_url_paths_from_model at 0x75202a07b7f0>
DEBUG     botocore.hooks                            Event before-parameter-build.s3.PutObject: calling handler <bound method S3RegionRedirectorv2.annotate_request_context of <botocore.utils.S3RegionRedirectorv2 object at 0x751f59e81e10>>
DEBUG     botocore.hooks                            Event before-parameter-build.s3.PutObject: calling handler <bound method ClientCreator._inject_s3_input_parameters of <botocore.client.ClientCreator object at 0x751f5a967130>>
DEBUG     botocore.hooks                            Event before-parameter-build.s3.PutObject: calling handler <function generate_idempotent_uuid at 0x75202a0797e0>
DEBUG     botocore.hooks                            Event before-endpoint-resolution.s3: calling handler <function customize_endpoint_resolver_builtins at 0x75202a07b9a0>
DEBUG     botocore.hooks                            Event before-endpoint-resolution.s3: calling handler <bound method S3RegionRedirectorv2.redirect_from_cache of <botocore.utils.S3RegionRedirectorv2 object at 0x751f59e81e10>>
DEBUG     botocore.regions                          Calling endpoint provider with parameters: {'Bucket': 'aiveilix', 'Region': 'auto', 'UseFIPS': False, 'UseDualStack': False, 'Endpoint': 'https://93d07d6cff38141aaf5eed882cda6725.r2.cloudflarestorage.com', 'ForcePathStyle': True, 'Accelerate': False, 'UseGlobalEndpoint': False, 'Key': 'layouts/1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7/layout.json', 'DisableMultiRegionAccessPoints': False, 'UseArnRegion': True}
DEBUG     botocore.regions                          Endpoint provider result: https://93d07d6cff38141aaf5eed882cda6725.r2.cloudflarestorage.com/aiveilix
DEBUG     botocore.regions                          Selecting from endpoint provider's list of auth schemes: "sigv4". User selected auth scheme is: "None"
DEBUG     botocore.regions                          Selected auth type "v4" as "v4" with signing context params: {'region': 'auto', 'signing_name': 's3', 'disableDoubleEncoding': True}
DEBUG     botocore.hooks                            Event before-call.s3.PutObject: calling handler <function conditionally_calculate_checksum at 0x75202a124160>
DEBUG     botocore.hooks                            Event before-call.s3.PutObject: calling handler <function add_expect_header at 0x75202a079cf0>
DEBUG     botocore.handlers                         Adding expect 100 continue header to request.
DEBUG     botocore.hooks                            Event before-call.s3.PutObject: calling handler <bound method S3ExpressIdentityResolver.apply_signing_cache_key of <botocore.utils.S3ExpressIdentityResolver object at 0x751f59e81e70>>
DEBUG     botocore.hooks                            Event before-call.s3.PutObject: calling handler <function add_recursion_detection_header at 0x75202a0793f0>
DEBUG     botocore.hooks                            Event before-call.s3.PutObject: calling handler <function add_query_compatibility_header at 0x75202a07be20>
DEBUG     botocore.hooks                            Event before-call.s3.PutObject: calling handler <function inject_api_version_header_if_needed at 0x75202a07b010>
DEBUG     botocore.endpoint                         Making request for OperationModel(name=PutObject) with params: {'url_path': '/layouts/1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7/layout.json', 'query_string': {}, 'method': 'PUT', 'headers': {'Content-Type': 'application/json', 'User-Agent': 'Boto3/1.35.85 md/Botocore#1.35.99 ua/2.0 os/linux#6.8.0-1048-gcp md/arch#x86_64 lang/python#3.10.12 md/pyimpl#CPython cfg/retry-mode#legacy Botocore/1.35.99', 'Content-MD5': 'E7P5Q1i3HRmOpiztAEBMsg==', 'Expect': '100-continue'}, 'body': <s3transfer.utils.ReadFileChunk object at 0x751f37ac2ad0>, 'auth_path': '/aiveilix/layouts/1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7/layout.json', 'url': 'https://93d07d6cff38141aaf5eed882cda6725.r2.cloudflarestorage.com/aiveilix/layouts/1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7/layout.json', 'context': {'client_region': 'auto', 'client_config': <botocore.config.Config object at 0x751f59e360b0>, 'has_streaming_input': True, 'auth_type': 'v4', 'unsigned_payload': None, 's3_redirect': {'redirected': False, 'bucket': 'aiveilix', 'params': {'Bucket': 'aiveilix', 'Key': 'layouts/1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7/layout.json', 'Body': <s3transfer.utils.ReadFileChunk object at 0x751f37ac2ad0>, 'ContentType': 'application/json'}}, 'input_params': {'Bucket': 'aiveilix', 'Key': 'layouts/1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7/layout.json'}, 'signing': {'region': 'auto', 'signing_name': 's3', 'disableDoubleEncoding': True}, 'endpoint_properties': {'authSchemes': [{'disableDoubleEncoding': True, 'name': 'sigv4', 'signingName': 's3', 'signingRegion': 'auto'}]}}}
DEBUG     botocore.hooks                            Event request-created.s3.PutObject: calling handler <function signal_not_transferring at 0x751f59ff8ca0>
DEBUG     botocore.hooks                            Event request-created.s3.PutObject: calling handler <bound method RequestSigner.handler of <botocore.signers.RequestSigner object at 0x751f59f9db40>>
DEBUG     botocore.hooks                            Event choose-signer.s3.PutObject: calling handler <function set_operation_specific_signer at 0x75202a079630>
DEBUG     botocore.hooks                            Event before-sign.s3.PutObject: calling handler <function remove_arn_from_signing_path at 0x75202a07b910>
DEBUG     botocore.hooks                            Event before-sign.s3.PutObject: calling handler <bound method S3ExpressIdentityResolver.resolve_s3express_identity of <botocore.utils.S3ExpressIdentityResolver object at 0x751f59e81e70>>
DEBUG     botocore.auth                             Calculating signature using v4 auth.
DEBUG     botocore.auth                             CanonicalRequest:
PUT
/aiveilix/layouts/1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7/layout.json

content-md5:E7P5Q1i3HRmOpiztAEBMsg==
content-type:application/json
host:93d07d6cff38141aaf5eed882cda6725.r2.cloudflarestorage.com
x-amz-content-sha256:UNSIGNED-PAYLOAD
x-amz-date:20260406T021450Z

content-md5;content-type;host;x-amz-content-sha256;x-amz-date
UNSIGNED-PAYLOAD
DEBUG     botocore.auth                             StringToSign:
AWS4-HMAC-SHA256
20260406T021450Z
20260406/auto/s3/aws4_request
8bd4fd1892f85f75ccaf212c750845d02a3d4310f793b2ff98bd395a56512c81
DEBUG     botocore.auth                             Signature:
5d5ec41263791aa7fca86c661c63df0419bf806fa317af60abf20541e77580d1
DEBUG     botocore.hooks                            Event request-created.s3.PutObject: calling handler <function signal_transferring at 0x751f59ff8d30>
DEBUG     botocore.hooks                            Event request-created.s3.PutObject: calling handler <function add_retry_headers at 0x75202a07b760>
DEBUG     botocore.endpoint                         Sending http request: <AWSPreparedRequest stream_output=False, method=PUT, url=https://93d07d6cff38141aaf5eed882cda6725.r2.cloudflarestorage.com/aiveilix/layouts/1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7/layout.json, headers={'Content-Type': b'application/json', 'User-Agent': b'Boto3/1.35.85 md/Botocore#1.35.99 ua/2.0 os/linux#6.8.0-1048-gcp md/arch#x86_64 lang/python#3.10.12 md/pyimpl#CPython cfg/retry-mode#legacy Botocore/1.35.99', 'Content-MD5': b'E7P5Q1i3HRmOpiztAEBMsg==', 'Expect': b'100-continue', 'X-Amz-Date': b'20260406T021450Z', 'X-Amz-Content-SHA256': b'UNSIGNED-PAYLOAD', 'Authorization': b'AWS4-HMAC-SHA256 Credential=a14d95abb63a7791c665f6833e04b1ea/20260406/auto/s3/aws4_request, SignedHeaders=content-md5;content-type;host;x-amz-content-sha256;x-amz-date, Signature=5d5ec41263791aa7fca86c661c63df0419bf806fa317af60abf20541e77580d1', 'amz-sdk-invocation-id': b'9b8e4048-1a21-47e6-a53b-02871710d715', 'amz-sdk-request': b'attempt=1', 'Content-Length': '343301'}>
DEBUG     botocore.httpsession                      Certificate path: /home/chaffanjutt/AIVEILIX/backend/.venv/lib/python3.10/site-packages/certifi/cacert.pem
DEBUG     botocore.awsrequest                       Waiting for 100 Continue response.
DEBUG     botocore.awsrequest                       100 Continue response seen, now sending request body.
DEBUG     urllib3.connectionpool                    https://93d07d6cff38141aaf5eed882cda6725.r2.cloudflarestorage.com:443 "PUT /aiveilix/layouts/1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7/layout.json HTTP/1.1" 200 0
DEBUG     botocore.hooks                            Event before-parse.s3.PutObject: calling handler <function _handle_200_error at 0x75202a07bc70>
DEBUG     botocore.hooks                            Event before-parse.s3.PutObject: calling handler <function handle_expires_header at 0x75202a07bac0>
DEBUG     botocore.parsers                          Response headers: {'Date': 'Mon, 06 Apr 2026 02:14:51 GMT', 'Content-Type': 'text/plain;charset=UTF-8', 'Content-Length': '0', 'Connection': 'keep-alive', 'ETag': '"13b3f94358b71d198ea62ced00404cb2"', 'x-amz-checksum-crc64nvme': 'TNTwdKIOMCc=', 'x-amz-version-id': '7e629f6dbed7e2888328116f97e3bddc', 'Vary': 'Accept-Encoding', 'Server': 'cloudflare', 'CF-RAY': '9e7d4807783e3f22-NRT'}
DEBUG     botocore.parsers                          Response body:
b''
DEBUG     botocore.hooks                            Event needs-retry.s3.PutObject: calling handler <function _update_status_code at 0x75202a07bd90>
DEBUG     botocore.hooks                            Event needs-retry.s3.PutObject: calling handler <botocore.retryhandler.RetryHandler object at 0x751f59e81d50>
DEBUG     botocore.retryhandler                     No retry needed.
DEBUG     botocore.hooks                            Event needs-retry.s3.PutObject: calling handler <bound method S3RegionRedirectorv2.redirect_from_error of <botocore.utils.S3RegionRedirectorv2 object at 0x751f59e81e10>>
DEBUG     s3transfer.utils                          Releasing acquire 0/None
INFO      app.services.storage.r2                   R2 upload OK: layouts/1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7/layout.json
2026-04-06 02:14:51,280 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:14:51,281 INFO sqlalchemy.engine.Engine INSERT INTO investigation_events (id, file_id, event, status, metadata) VALUES ($1::UUID, $2::UUID, $3::VARCHAR, $4::event_status, $5::JSONB) RETURNING investigation_events.created_at
INFO      sqlalchemy.engine.Engine                  INSERT INTO investigation_events (id, file_id, event, status, metadata) VALUES ($1::UUID, $2::UUID, $3::VARCHAR, $4::event_status, $5::JSONB) RETURNING investigation_events.created_at
2026-04-06 02:14:51,281 INFO sqlalchemy.engine.Engine [cached since 25.58s ago] (UUID('32e6fc04-9a23-4002-9f59-c6b4ab32a28c'), UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'), 'layout_json_created', 'completed', '{"trace_run_id": "d313c038-8766-431e-848d-542087af1456", "trigger_source": "upload", "stage": "layout_upload", "sequence": 15, "recorded_at": "2026-04-06T02:14:51.277346+00:00", "r2_key": "layouts/1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7/layout.json", "duration_ms": 532}')
INFO      sqlalchemy.engine.Engine                  [cached since 25.58s ago] (UUID('32e6fc04-9a23-4002-9f59-c6b4ab32a28c'), UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'), 'layout_json_created', 'completed', '{"trace_run_id": "d313c038-8766-431e-848d-542087af1456", "trigger_source": "upload", "stage": "layout_upload", "sequence": 15, "recorded_at": "2026-04-06T02:14:51.277346+00:00", "r2_key": "layouts/1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7/layout.json", "duration_ms": 532}')
2026-04-06 02:14:51,284 INFO sqlalchemy.engine.Engine COMMIT
INFO      sqlalchemy.engine.Engine                  COMMIT
INFO      app.services.pipeline.orchestrator        pipeline_trace file=1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7 trace=d313c038-8766-431e-848d-542087af1456 event=layout_json_created stage=layout_upload status=completed metadata={'trace_run_id': 'd313c038-8766-431e-848d-542087af1456', 'trigger_source': 'upload', 'stage': 'layout_upload', 'sequence': 15, 'recorded_at': '2026-04-06T02:14:51.277346+00:00', 'r2_key': 'layouts/1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7/layout.json', 'duration_ms': 532}
2026-04-06 02:14:51,290 INFO sqlalchemy.engine.Engine UPDATE files SET layout_json_path=$1::VARCHAR, page_count=$2::INTEGER, updated_at=now() WHERE files.id = $3::UUID
INFO      sqlalchemy.engine.Engine                  UPDATE files SET layout_json_path=$1::VARCHAR, page_count=$2::INTEGER, updated_at=now() WHERE files.id = $3::UUID
2026-04-06 02:14:51,290 INFO sqlalchemy.engine.Engine [generated in 0.00073s] ('layouts/1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7/layout.json', 1, UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'))
INFO      sqlalchemy.engine.Engine                  [generated in 0.00073s] ('layouts/1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7/layout.json', 1, UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'))
2026-04-06 02:14:51,297 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:14:51,298 INFO sqlalchemy.engine.Engine INSERT INTO investigation_events (id, file_id, event, status, metadata) VALUES ($1::UUID, $2::UUID, $3::VARCHAR, $4::event_status, $5::JSONB) RETURNING investigation_events.created_at
INFO      sqlalchemy.engine.Engine                  INSERT INTO investigation_events (id, file_id, event, status, metadata) VALUES ($1::UUID, $2::UUID, $3::VARCHAR, $4::event_status, $5::JSONB) RETURNING investigation_events.created_at
2026-04-06 02:14:51,299 INFO sqlalchemy.engine.Engine [cached since 25.59s ago] (UUID('51fe3559-5510-482b-899e-4e4955e743bb'), UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'), 'chunking_started', 'started', '{"trace_run_id": "d313c038-8766-431e-848d-542087af1456", "trigger_source": "upload", "stage": "chunking", "sequence": 16, "recorded_at": "2026-04-06T02:14:51.295044+00:00"}')
INFO      sqlalchemy.engine.Engine                  [cached since 25.59s ago] (UUID('51fe3559-5510-482b-899e-4e4955e743bb'), UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'), 'chunking_started', 'started', '{"trace_run_id": "d313c038-8766-431e-848d-542087af1456", "trigger_source": "upload", "stage": "chunking", "sequence": 16, "recorded_at": "2026-04-06T02:14:51.295044+00:00"}')
2026-04-06 02:14:51,302 INFO sqlalchemy.engine.Engine COMMIT
INFO      sqlalchemy.engine.Engine                  COMMIT
INFO      app.services.pipeline.orchestrator        pipeline_trace file=1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7 trace=d313c038-8766-431e-848d-542087af1456 event=chunking_started stage=chunking status=started metadata={'trace_run_id': 'd313c038-8766-431e-848d-542087af1456', 'trigger_source': 'upload', 'stage': 'chunking', 'sequence': 16, 'recorded_at': '2026-04-06T02:14:51.295044+00:00'}
INFO      app.services.processing.chunker           Chunker produced 2490 chunks for file 1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7
2026-04-06 02:14:51,576 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:14:51,577 INFO sqlalchemy.engine.Engine INSERT INTO investigation_events (id, file_id, event, status, metadata) VALUES ($1::UUID, $2::UUID, $3::VARCHAR, $4::event_status, $5::JSONB) RETURNING investigation_events.created_at
INFO      sqlalchemy.engine.Engine                  INSERT INTO investigation_events (id, file_id, event, status, metadata) VALUES ($1::UUID, $2::UUID, $3::VARCHAR, $4::event_status, $5::JSONB) RETURNING investigation_events.created_at
2026-04-06 02:14:51,577 INFO sqlalchemy.engine.Engine [cached since 25.87s ago] (UUID('c575d399-54f2-428b-bf55-94e4e269baa3'), UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'), 'chunking_completed', 'completed', '{"trace_run_id": "d313c038-8766-431e-848d-542087af1456", "trigger_source": "upload", "stage": "chunking", "sequence": 17, "recorded_at": "2026-04-06T02:14:51.573344+00:00", "chunks": 2490, "duration_ms": 278}')
INFO      sqlalchemy.engine.Engine                  [cached since 25.87s ago] (UUID('c575d399-54f2-428b-bf55-94e4e269baa3'), UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'), 'chunking_completed', 'completed', '{"trace_run_id": "d313c038-8766-431e-848d-542087af1456", "trigger_source": "upload", "stage": "chunking", "sequence": 17, "recorded_at": "2026-04-06T02:14:51.573344+00:00", "chunks": 2490, "duration_ms": 278}')
2026-04-06 02:14:51,580 INFO sqlalchemy.engine.Engine COMMIT
INFO      sqlalchemy.engine.Engine                  COMMIT
INFO      app.services.pipeline.orchestrator        pipeline_trace file=1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7 trace=d313c038-8766-431e-848d-542087af1456 event=chunking_completed stage=chunking status=completed metadata={'trace_run_id': 'd313c038-8766-431e-848d-542087af1456', 'trigger_source': 'upload', 'stage': 'chunking', 'sequence': 17, 'recorded_at': '2026-04-06T02:14:51.573344+00:00', 'chunks': 2490, 'duration_ms': 278}
2026-04-06 02:14:51,586 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:14:51,587 INFO sqlalchemy.engine.Engine INSERT INTO investigation_events (id, file_id, event, status, metadata) VALUES ($1::UUID, $2::UUID, $3::VARCHAR, $4::event_status, $5::JSONB) RETURNING investigation_events.created_at
INFO      sqlalchemy.engine.Engine                  INSERT INTO investigation_events (id, file_id, event, status, metadata) VALUES ($1::UUID, $2::UUID, $3::VARCHAR, $4::event_status, $5::JSONB) RETURNING investigation_events.created_at
2026-04-06 02:14:51,587 INFO sqlalchemy.engine.Engine [cached since 25.88s ago] (UUID('0ff9f021-ebf4-475b-892c-c63544c23d14'), UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'), 'embedding_started', 'started', '{"trace_run_id": "d313c038-8766-431e-848d-542087af1456", "trigger_source": "upload", "stage": "embedding_pipeline", "sequence": 18, "recorded_at": "2026-04-06T02:14:51.584080+00:00", "chunks": 2491}')
INFO      sqlalchemy.engine.Engine                  [cached since 25.88s ago] (UUID('0ff9f021-ebf4-475b-892c-c63544c23d14'), UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'), 'embedding_started', 'started', '{"trace_run_id": "d313c038-8766-431e-848d-542087af1456", "trigger_source": "upload", "stage": "embedding_pipeline", "sequence": 18, "recorded_at": "2026-04-06T02:14:51.584080+00:00", "chunks": 2491}')
2026-04-06 02:14:51,590 INFO sqlalchemy.engine.Engine COMMIT
INFO      sqlalchemy.engine.Engine                  COMMIT
INFO      app.services.pipeline.orchestrator        pipeline_trace file=1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7 trace=d313c038-8766-431e-848d-542087af1456 event=embedding_started stage=embedding_pipeline status=started metadata={'trace_run_id': 'd313c038-8766-431e-848d-542087af1456', 'trigger_source': 'upload', 'stage': 'embedding_pipeline', 'sequence': 18, 'recorded_at': '2026-04-06T02:14:51.584080+00:00', 'chunks': 2491}
WARNING   app.services.pipeline.orchestrator        Quality gate: dropped 31/2491 garbled chunks for file 1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7 before embedding
2026-04-06 02:14:52,484 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:14:52,485 INFO sqlalchemy.engine.Engine INSERT INTO investigation_events (id, file_id, event, status, metadata) VALUES ($1::UUID, $2::UUID, $3::VARCHAR, $4::event_status, $5::JSONB) RETURNING investigation_events.created_at
INFO      sqlalchemy.engine.Engine                  INSERT INTO investigation_events (id, file_id, event, status, metadata) VALUES ($1::UUID, $2::UUID, $3::VARCHAR, $4::event_status, $5::JSONB) RETURNING investigation_events.created_at
2026-04-06 02:14:52,486 INFO sqlalchemy.engine.Engine [cached since 26.78s ago] (UUID('aad9cb90-409b-459a-81c6-2fe01e34997a'), UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'), 'text_embedding_started', 'started', '{"trace_run_id": "d313c038-8766-431e-848d-542087af1456", "trigger_source": "upload", "stage": "text_embeddings", "sequence": 19, "recorded_at": "2026-04-06T02:14:52.481107+00:00", "chunk_count": 2460}')
INFO      sqlalchemy.engine.Engine                  [cached since 26.78s ago] (UUID('aad9cb90-409b-459a-81c6-2fe01e34997a'), UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'), 'text_embedding_started', 'started', '{"trace_run_id": "d313c038-8766-431e-848d-542087af1456", "trigger_source": "upload", "stage": "text_embeddings", "sequence": 19, "recorded_at": "2026-04-06T02:14:52.481107+00:00", "chunk_count": 2460}')
2026-04-06 02:14:52,488 INFO sqlalchemy.engine.Engine COMMIT
INFO      sqlalchemy.engine.Engine                  COMMIT
INFO      app.services.pipeline.orchestrator        pipeline_trace file=1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7 trace=d313c038-8766-431e-848d-542087af1456 event=text_embedding_started stage=text_embeddings status=started metadata={'trace_run_id': 'd313c038-8766-431e-848d-542087af1456', 'trigger_source': 'upload', 'stage': 'text_embeddings', 'sequence': 19, 'recorded_at': '2026-04-06T02:14:52.481107+00:00', 'chunk_count': 2460}
INFO      app.services.embeddings.text_embeddings   Loading BGE-M3 model (first call — may take a moment)...
DEBUG     urllib3.connectionpool                    Starting new HTTPS connection (1): huggingface.co:443
DEBUG     urllib3.connectionpool                    https://huggingface.co:443 "HEAD /BAAI/bge-m3/resolve/main/tokenizer_config.json HTTP/1.1" 307 0
DEBUG     urllib3.connectionpool                    https://huggingface.co:443 "HEAD /api/resolve-cache/models/BAAI/bge-m3/5617a9f61b028005a4858fdac845db406aefb181/tokenizer_config.json HTTP/1.1" 200 0
2026-04-06 02:14:56,132 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:14:56,133 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:14:56,133 INFO sqlalchemy.engine.Engine [cached since 44.93s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 44.93s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:14:56,138 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
2026-04-06 02:14:56,138 INFO sqlalchemy.engine.Engine [cached since 44.91s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 44.91s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:14:56,141 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:14:56,191 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:14:56,192 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:14:56,193 INFO sqlalchemy.engine.Engine [cached since 44.99s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 44.99s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:14:56,196 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
2026-04-06 02:14:56,196 INFO sqlalchemy.engine.Engine [cached since 44.97s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 44.97s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:14:56,199 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
DEBUG     urllib3.connectionpool                    https://huggingface.co:443 "GET /api/models/BAAI/bge-m3/revision/main HTTP/1.1" 200 None
Fetching 30 files: 100%|█████████████████████████████████████████████████████████████████████████| 30/30 [00:00<00:00, 5688.73it/s]
2026-04-06 02:14:59,272 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:14:59,273 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:14:59,275 INFO sqlalchemy.engine.Engine [cached since 48.07s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 48.07s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:14:59,280 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
2026-04-06 02:14:59,280 INFO sqlalchemy.engine.Engine [cached since 48.05s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 48.05s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:14:59,283 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:15:02,321 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:15:02,322 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:15:02,322 INFO sqlalchemy.engine.Engine [cached since 51.12s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 51.12s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:15:02,325 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
2026-04-06 02:15:02,326 INFO sqlalchemy.engine.Engine [cached since 51.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 51.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:15:02,330 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
INFO      app.services.embeddings.text_embeddings   BGE-M3 model loaded.
pre tokenize: 100%|█████████████████████████████████████████████████████████████████████████████| 205/205 [00:01<00:00, 152.26it/s]
You're using a XLMRobertaTokenizerFast tokenizer. Please note that with a fast tokenizer, using the `__call__` method is faster than using a method to encode the text followed by a call to the `pad` method to get a padded encoding.
2026-04-06 02:15:06,273 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:15:06,274 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:15:06,274 INFO sqlalchemy.engine.Engine [cached since 55.07s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 55.07s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:15:06,277 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
2026-04-06 02:15:06,278 INFO sqlalchemy.engine.Engine [cached since 55.05s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 55.05s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:15:06,280 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:15:10,274 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:15:10,275 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:15:10,275 INFO sqlalchemy.engine.Engine [cached since 59.07s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 59.07s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:15:10,279 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
2026-04-06 02:15:10,280 INFO sqlalchemy.engine.Engine [cached since 59.05s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 59.05s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:15:10,284 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:15:14,274 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:15:14,275 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:15:14,276 INFO sqlalchemy.engine.Engine [cached since 63.07s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 63.07s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:15:14,280 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
2026-04-06 02:15:14,280 INFO sqlalchemy.engine.Engine [cached since 63.05s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 63.05s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:15:14,283 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:15:18,274 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:15:18,276 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:15:18,277 INFO sqlalchemy.engine.Engine [cached since 67.07s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 67.07s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:15:18,281 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
2026-04-06 02:15:18,282 INFO sqlalchemy.engine.Engine [cached since 67.06s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 67.06s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:15:18,285 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:15:22,275 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:15:22,276 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:15:22,277 INFO sqlalchemy.engine.Engine [cached since 71.07s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 71.07s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:15:22,281 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
2026-04-06 02:15:22,282 INFO sqlalchemy.engine.Engine [cached since 71.06s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 71.06s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:15:22,285 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:15:26,275 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:15:26,276 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:15:26,276 INFO sqlalchemy.engine.Engine [cached since 75.07s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 75.07s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:15:26,280 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
2026-04-06 02:15:26,282 INFO sqlalchemy.engine.Engine [cached since 75.06s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 75.06s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:15:26,284 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:15:29,317 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:15:29,318 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:15:29,318 INFO sqlalchemy.engine.Engine [cached since 78.11s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 78.11s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:15:29,322 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
2026-04-06 02:15:29,322 INFO sqlalchemy.engine.Engine [cached since 78.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 78.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:15:29,325 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:15:33,274 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:15:33,275 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:15:33,275 INFO sqlalchemy.engine.Engine [cached since 82.07s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 82.07s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:15:33,279 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
2026-04-06 02:15:33,280 INFO sqlalchemy.engine.Engine [cached since 82.05s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 82.05s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:15:33,284 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:15:37,276 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:15:37,277 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:15:37,278 INFO sqlalchemy.engine.Engine [cached since 86.07s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 86.07s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:15:37,281 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
2026-04-06 02:15:37,281 INFO sqlalchemy.engine.Engine [cached since 86.06s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 86.06s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:15:37,284 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:15:41,274 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:15:41,275 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:15:41,275 INFO sqlalchemy.engine.Engine [cached since 90.07s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 90.07s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:15:41,279 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
2026-04-06 02:15:41,280 INFO sqlalchemy.engine.Engine [cached since 90.05s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 90.05s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:15:41,283 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:15:45,274 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:15:45,275 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:15:45,276 INFO sqlalchemy.engine.Engine [cached since 94.07s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 94.07s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:15:45,281 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
2026-04-06 02:15:45,282 INFO sqlalchemy.engine.Engine [cached since 94.06s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 94.06s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:15:45,286 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:15:48,318 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:15:48,321 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:15:48,323 INFO sqlalchemy.engine.Engine [cached since 97.12s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 97.12s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:15:48,327 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
2026-04-06 02:15:48,328 INFO sqlalchemy.engine.Engine [cached since 97.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 97.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:15:48,331 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:15:51,362 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:15:51,363 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:15:51,364 INFO sqlalchemy.engine.Engine [cached since 100.2s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 100.2s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:15:51,368 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
2026-04-06 02:15:51,368 INFO sqlalchemy.engine.Engine [cached since 100.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 100.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:15:51,370 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:15:54,403 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:15:54,404 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:15:54,405 INFO sqlalchemy.engine.Engine [cached since 103.2s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 103.2s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:15:54,411 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
2026-04-06 02:15:54,412 INFO sqlalchemy.engine.Engine [cached since 103.2s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 103.2s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:15:54,415 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:15:57,453 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:15:57,455 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:15:57,457 INFO sqlalchemy.engine.Engine [cached since 106.3s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 106.3s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:15:57,461 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
2026-04-06 02:15:57,462 INFO sqlalchemy.engine.Engine [cached since 106.2s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 106.2s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:15:57,465 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:16:01,275 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:16:01,277 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:16:01,278 INFO sqlalchemy.engine.Engine [cached since 110.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 110.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:16:01,287 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
2026-04-06 02:16:01,288 INFO sqlalchemy.engine.Engine [cached since 110.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 110.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:16:01,291 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:16:05,275 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:16:05,276 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:16:05,276 INFO sqlalchemy.engine.Engine [cached since 114.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 114.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:16:05,280 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
2026-04-06 02:16:05,282 INFO sqlalchemy.engine.Engine [cached since 114.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 114.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:16:05,285 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:16:09,274 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:16:09,275 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:16:09,277 INFO sqlalchemy.engine.Engine [cached since 118.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 118.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:16:09,280 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
2026-04-06 02:16:09,281 INFO sqlalchemy.engine.Engine [cached since 118.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 118.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:16:09,284 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:16:13,273 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:16:13,274 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:16:13,275 INFO sqlalchemy.engine.Engine [cached since 122.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 122.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:16:13,278 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
2026-04-06 02:16:13,280 INFO sqlalchemy.engine.Engine [cached since 122.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 122.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:16:13,283 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:16:17,276 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:16:17,277 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:16:17,277 INFO sqlalchemy.engine.Engine [cached since 126.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 126.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:16:17,282 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
2026-04-06 02:16:17,283 INFO sqlalchemy.engine.Engine [cached since 126.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 126.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:16:17,286 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:16:20,606 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:16:20,607 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:16:20,607 INFO sqlalchemy.engine.Engine [cached since 129.4s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 129.4s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:16:20,610 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
2026-04-06 02:16:20,611 INFO sqlalchemy.engine.Engine [cached since 129.4s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 129.4s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:16:20,613 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:16:23,646 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:16:23,647 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:16:23,647 INFO sqlalchemy.engine.Engine [cached since 132.4s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 132.4s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:16:23,650 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
2026-04-06 02:16:23,651 INFO sqlalchemy.engine.Engine [cached since 132.4s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 132.4s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:16:23,654 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:16:27,274 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:16:27,275 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:16:27,275 INFO sqlalchemy.engine.Engine [cached since 136.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 136.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:16:27,279 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
2026-04-06 02:16:27,280 INFO sqlalchemy.engine.Engine [cached since 136.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 136.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:16:27,283 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:16:30,319 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:16:30,320 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:16:30,320 INFO sqlalchemy.engine.Engine [cached since 139.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 139.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:16:30,324 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
2026-04-06 02:16:30,325 INFO sqlalchemy.engine.Engine [cached since 139.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 139.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:16:30,328 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:16:34,274 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:16:34,275 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:16:34,275 INFO sqlalchemy.engine.Engine [cached since 143.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 143.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:16:34,280 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
2026-04-06 02:16:34,282 INFO sqlalchemy.engine.Engine [cached since 143.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 143.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:16:34,285 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:16:37,318 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:16:37,319 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:16:37,320 INFO sqlalchemy.engine.Engine [cached since 146.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 146.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:16:37,323 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
2026-04-06 02:16:37,324 INFO sqlalchemy.engine.Engine [cached since 146.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 146.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:16:37,326 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:16:40,363 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:16:40,364 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:16:40,364 INFO sqlalchemy.engine.Engine [cached since 149.2s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 149.2s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:16:40,367 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
2026-04-06 02:16:40,368 INFO sqlalchemy.engine.Engine [cached since 149.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 149.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:16:40,370 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:16:43,403 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:16:43,404 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:16:43,404 INFO sqlalchemy.engine.Engine [cached since 152.2s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 152.2s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:16:43,407 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
2026-04-06 02:16:43,408 INFO sqlalchemy.engine.Engine [cached since 152.2s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 152.2s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:16:43,410 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:16:46,444 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:16:46,444 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:16:46,445 INFO sqlalchemy.engine.Engine [cached since 155.2s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 155.2s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:16:46,448 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
2026-04-06 02:16:46,448 INFO sqlalchemy.engine.Engine [cached since 155.2s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 155.2s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:16:46,450 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:16:49,480 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:16:49,481 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:16:49,482 INFO sqlalchemy.engine.Engine [cached since 158.3s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 158.3s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:16:49,485 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
2026-04-06 02:16:49,486 INFO sqlalchemy.engine.Engine [cached since 158.3s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 158.3s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:16:49,488 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:16:49,523 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:16:49,524 INFO sqlalchemy.engine.Engine SELECT conversations.id, conversations.user_id, conversations.bucket_id, conversations.title, conversations.web_search_mode, conversations.follow_up_mode, conversations.is_pinned, conversations.created_at, conversations.updated_at 
FROM conversations 
WHERE conversations.id = $1::UUID AND conversations.bucket_id = $2::UUID AND conversations.user_id = $3::UUID
INFO      sqlalchemy.engine.Engine                  SELECT conversations.id, conversations.user_id, conversations.bucket_id, conversations.title, conversations.web_search_mode, conversations.follow_up_mode, conversations.is_pinned, conversations.created_at, conversations.updated_at 
FROM conversations 
WHERE conversations.id = $1::UUID AND conversations.bucket_id = $2::UUID AND conversations.user_id = $3::UUID
2026-04-06 02:16:49,524 INFO sqlalchemy.engine.Engine [cached since 158s ago] (UUID('64984f1b-3917-46f0-9555-e0ef067c040b'), UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'), UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'))
INFO      sqlalchemy.engine.Engine                  [cached since 158s ago] (UUID('64984f1b-3917-46f0-9555-e0ef067c040b'), UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'), UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'))
2026-04-06 02:16:49,527 INFO sqlalchemy.engine.Engine SELECT profiles.id, profiles.user_id, profiles.full_name, profiles.avatar_url, profiles.bio, profiles.theme, profiles.language, profiles.timezone, profiles.preferred_llm, profiles.follow_up_mode, profiles.use_case, profiles.referral_source, profiles.updated_at 
FROM profiles 
WHERE profiles.user_id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT profiles.id, profiles.user_id, profiles.full_name, profiles.avatar_url, profiles.bio, profiles.theme, profiles.language, profiles.timezone, profiles.preferred_llm, profiles.follow_up_mode, profiles.use_case, profiles.referral_source, profiles.updated_at 
FROM profiles 
WHERE profiles.user_id = $1::UUID
2026-04-06 02:16:49,528 INFO sqlalchemy.engine.Engine [cached since 168.9s ago] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'),)
INFO      sqlalchemy.engine.Engine                  [cached since 168.9s ago] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'),)
INFO      app.services.agent.service                [USER] hey read this and let me know hst is in it tahnsk
2026-04-06 02:16:49,735 INFO sqlalchemy.engine.Engine INSERT INTO messages (id, conversation_id, parent_message_id, role, content, chunks_used, token_count, embedding_status, agent_wrote_file_id) VALUES ($1::UUID, $2::UUID, $3::UUID, $4::message_role, $5::VARCHAR, $6::JSONB, $7::INTEGER, $8::embedding_status, $9::UUID) RETURNING messages.created_at
INFO      sqlalchemy.engine.Engine                  INSERT INTO messages (id, conversation_id, parent_message_id, role, content, chunks_used, token_count, embedding_status, agent_wrote_file_id) VALUES ($1::UUID, $2::UUID, $3::UUID, $4::message_role, $5::VARCHAR, $6::JSONB, $7::INTEGER, $8::embedding_status, $9::UUID) RETURNING messages.created_at
2026-04-06 02:16:49,736 INFO sqlalchemy.engine.Engine [generated in 0.00085s] (UUID('f0fe4dde-e09c-4504-80b4-385718c58815'), UUID('64984f1b-3917-46f0-9555-e0ef067c040b'), None, 'user', 'hey read this and let me know hst is in it tahnsk', '[]', 15, 'pending', None)
INFO      sqlalchemy.engine.Engine                  [generated in 0.00085s] (UUID('f0fe4dde-e09c-4504-80b4-385718c58815'), UUID('64984f1b-3917-46f0-9555-e0ef067c040b'), None, 'user', 'hey read this and let me know hst is in it tahnsk', '[]', 15, 'pending', None)
WARNING   app.services.agent.llm                    [LLM] preferred provider claude unavailable, falling back to deepseek
INFO      app.services.agent.llm                    [LLM] provider=deepseek
INFO      app.services.agent.llm                    [LLM] deepseek → 137 chars
2026-04-06 02:16:52,467 INFO sqlalchemy.engine.Engine INSERT INTO messages (id, conversation_id, parent_message_id, role, content, chunks_used, token_count, embedding_status, agent_wrote_file_id) VALUES ($1::UUID, $2::UUID, $3::UUID, $4::message_role, $5::VARCHAR, $6::JSONB, $7::INTEGER, $8::embedding_status, $9::UUID) RETURNING messages.created_at
INFO      sqlalchemy.engine.Engine                  INSERT INTO messages (id, conversation_id, parent_message_id, role, content, chunks_used, token_count, embedding_status, agent_wrote_file_id) VALUES ($1::UUID, $2::UUID, $3::UUID, $4::message_role, $5::VARCHAR, $6::JSONB, $7::INTEGER, $8::embedding_status, $9::UUID) RETURNING messages.created_at
2026-04-06 02:16:52,467 INFO sqlalchemy.engine.Engine [generated in 0.00139s] (UUID('699b43a0-d735-4d10-b8ee-f14df642e049'), UUID('64984f1b-3917-46f0-9555-e0ef067c040b'), UUID('f0fe4dde-e09c-4504-80b4-385718c58815'), 'assistant', "Hey! I don't see any document in your bucket to read from — if you upload something, I’ll gladly take a look and tell you what’s in it! 😊\n\n---\n\nSources:\nNo document or web sources were used.", '[]', 48, 'pending', None)
INFO      sqlalchemy.engine.Engine                  [generated in 0.00139s] (UUID('699b43a0-d735-4d10-b8ee-f14df642e049'), UUID('64984f1b-3917-46f0-9555-e0ef067c040b'), UUID('f0fe4dde-e09c-4504-80b4-385718c58815'), 'assistant', "Hey! I don't see any document in your bucket to read from — if you upload something, I’ll gladly take a look and tell you what’s in it! 😊\n\n---\n\nSources:\nNo document or web sources were used.", '[]', 48, 'pending', None)
2026-04-06 02:16:55,052 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:16:55,053 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:16:55,053 INFO sqlalchemy.engine.Engine [cached since 163.9s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 163.9s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:16:55,057 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
2026-04-06 02:16:55,058 INFO sqlalchemy.engine.Engine [cached since 163.8s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 163.8s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:16:55,062 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
DEBUG     app.services.embeddings.text_embeddings   BGE-M3 encoded 1 texts
2026-04-06 02:16:59,259 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:16:59,260 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:16:59,261 INFO sqlalchemy.engine.Engine [cached since 168.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 168.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:16:59,343 INFO sqlalchemy.engine.Engine INSERT INTO conversation_chunks (id, conversation_id, message_id, bucket_id, user_id, role, content, chunk_index, token_count, status) VALUES ($1::UUID, $2::UUID, $3::UUID, $4::UUID, $5::UUID, $6::message_role, $7::VARCHAR, $8::INTEGER, $9::INTEGER, $10::embedding_status) RETURNING conversation_chunks.created_at
INFO      sqlalchemy.engine.Engine                  INSERT INTO conversation_chunks (id, conversation_id, message_id, bucket_id, user_id, role, content, chunk_index, token_count, status) VALUES ($1::UUID, $2::UUID, $3::UUID, $4::UUID, $5::UUID, $6::message_role, $7::VARCHAR, $8::INTEGER, $9::INTEGER, $10::embedding_status) RETURNING conversation_chunks.created_at
2026-04-06 02:16:59,344 INFO sqlalchemy.engine.Engine [generated in 0.00120s] (UUID('55e3e935-92e2-48de-9701-7489bdaf3c08'), UUID('64984f1b-3917-46f0-9555-e0ef067c040b'), UUID('f0fe4dde-e09c-4504-80b4-385718c58815'), UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'), UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), 'user', 'User: hey read this and let me know hst is in it tahnsk', 0, 17, 'pending')
INFO      sqlalchemy.engine.Engine                  [generated in 0.00120s] (UUID('55e3e935-92e2-48de-9701-7489bdaf3c08'), UUID('64984f1b-3917-46f0-9555-e0ef067c040b'), UUID('f0fe4dde-e09c-4504-80b4-385718c58815'), UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'), UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), 'user', 'User: hey read this and let me know hst is in it tahnsk', 0, 17, 'pending')
2026-04-06 02:16:59,348 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
2026-04-06 02:16:59,349 INFO sqlalchemy.engine.Engine [cached since 168.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 168.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:16:59,352 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:17:03,398 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:17:03,399 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:17:03,402 INFO sqlalchemy.engine.Engine [cached since 172.2s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 172.2s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:17:03,410 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
2026-04-06 02:17:03,414 INFO sqlalchemy.engine.Engine [cached since 172.2s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 172.2s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:17:03,424 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
DEBUG     app.services.embeddings.text_embeddings   BGE-M3 encoded 1 texts
2026-04-06 02:17:04,163 INFO sqlalchemy.engine.Engine UPDATE messages SET embedding_status=$1::embedding_status WHERE messages.id = $2::UUID
INFO      sqlalchemy.engine.Engine                  UPDATE messages SET embedding_status=$1::embedding_status WHERE messages.id = $2::UUID
2026-04-06 02:17:04,164 INFO sqlalchemy.engine.Engine [generated in 0.00105s] ('embedded', UUID('f0fe4dde-e09c-4504-80b4-385718c58815'))
INFO      sqlalchemy.engine.Engine                  [generated in 0.00105s] ('embedded', UUID('f0fe4dde-e09c-4504-80b4-385718c58815'))
2026-04-06 02:17:04,185 INFO sqlalchemy.engine.Engine UPDATE conversation_chunks SET status=$1::embedding_status WHERE conversation_chunks.id = $2::UUID
INFO      sqlalchemy.engine.Engine                  UPDATE conversation_chunks SET status=$1::embedding_status WHERE conversation_chunks.id = $2::UUID
2026-04-06 02:17:04,187 INFO sqlalchemy.engine.Engine [generated in 0.00181s] ('embedded', UUID('55e3e935-92e2-48de-9701-7489bdaf3c08'))
INFO      sqlalchemy.engine.Engine                  [generated in 0.00181s] ('embedded', UUID('55e3e935-92e2-48de-9701-7489bdaf3c08'))
2026-04-06 02:17:04,193 INFO sqlalchemy.engine.Engine INSERT INTO conversation_chunks (id, conversation_id, message_id, bucket_id, user_id, role, content, chunk_index, token_count, status) VALUES ($1::UUID, $2::UUID, $3::UUID, $4::UUID, $5::UUID, $6::message_role, $7::VARCHAR, $8::INTEGER, $9::INTEGER, $10::embedding_status) RETURNING conversation_chunks.created_at
INFO      sqlalchemy.engine.Engine                  INSERT INTO conversation_chunks (id, conversation_id, message_id, bucket_id, user_id, role, content, chunk_index, token_count, status) VALUES ($1::UUID, $2::UUID, $3::UUID, $4::UUID, $5::UUID, $6::message_role, $7::VARCHAR, $8::INTEGER, $9::INTEGER, $10::embedding_status) RETURNING conversation_chunks.created_at
2026-04-06 02:17:04,194 INFO sqlalchemy.engine.Engine [cached since 4.851s ago] (UUID('73c5ecaf-a052-4e6d-afe3-3e63fc882200'), UUID('64984f1b-3917-46f0-9555-e0ef067c040b'), UUID('699b43a0-d735-4d10-b8ee-f14df642e049'), UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'), UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), 'assistant', "Assistant: Hey! I don't see any document in your bucket to read from — if you upload something, I’ll gladly take a look and tell you what’s in it! 😊\n\n---\n\nSources:\nNo document or web sources were used.", 0, 50, 'pending')
INFO      sqlalchemy.engine.Engine                  [cached since 4.851s ago] (UUID('73c5ecaf-a052-4e6d-afe3-3e63fc882200'), UUID('64984f1b-3917-46f0-9555-e0ef067c040b'), UUID('699b43a0-d735-4d10-b8ee-f14df642e049'), UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'), UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), 'assistant', "Assistant: Hey! I don't see any document in your bucket to read from — if you upload something, I’ll gladly take a look and tell you what’s in it! 😊\n\n---\n\nSources:\nNo document or web sources were used.", 0, 50, 'pending')
2026-04-06 02:17:04,213 INFO sqlalchemy.engine.Engine UPDATE messages SET embedding_status=$1::embedding_status WHERE messages.id = $2::UUID
INFO      sqlalchemy.engine.Engine                  UPDATE messages SET embedding_status=$1::embedding_status WHERE messages.id = $2::UUID
2026-04-06 02:17:04,214 INFO sqlalchemy.engine.Engine [cached since 0.05101s ago] ('embedded', UUID('699b43a0-d735-4d10-b8ee-f14df642e049'))
INFO      sqlalchemy.engine.Engine                  [cached since 0.05101s ago] ('embedded', UUID('699b43a0-d735-4d10-b8ee-f14df642e049'))
2026-04-06 02:17:04,216 INFO sqlalchemy.engine.Engine UPDATE conversation_chunks SET status=$1::embedding_status WHERE conversation_chunks.id = $2::UUID
INFO      sqlalchemy.engine.Engine                  UPDATE conversation_chunks SET status=$1::embedding_status WHERE conversation_chunks.id = $2::UUID
2026-04-06 02:17:04,217 INFO sqlalchemy.engine.Engine [cached since 0.03169s ago] ('embedded', UUID('73c5ecaf-a052-4e6d-afe3-3e63fc882200'))
INFO      sqlalchemy.engine.Engine                  [cached since 0.03169s ago] ('embedded', UUID('73c5ecaf-a052-4e6d-afe3-3e63fc882200'))
2026-04-06 02:17:04,220 INFO sqlalchemy.engine.Engine COMMIT
INFO      sqlalchemy.engine.Engine                  COMMIT
2026-04-06 02:17:04,226 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:17:04,227 INFO sqlalchemy.engine.Engine SELECT conversations.id, conversations.user_id, conversations.bucket_id, conversations.title, conversations.web_search_mode, conversations.follow_up_mode, conversations.is_pinned, conversations.created_at, conversations.updated_at 
FROM conversations 
WHERE conversations.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT conversations.id, conversations.user_id, conversations.bucket_id, conversations.title, conversations.web_search_mode, conversations.follow_up_mode, conversations.is_pinned, conversations.created_at, conversations.updated_at 
FROM conversations 
WHERE conversations.id = $1::UUID
2026-04-06 02:17:04,228 INFO sqlalchemy.engine.Engine [cached since 172.8s ago] (UUID('64984f1b-3917-46f0-9555-e0ef067c040b'),)
INFO      sqlalchemy.engine.Engine                  [cached since 172.8s ago] (UUID('64984f1b-3917-46f0-9555-e0ef067c040b'),)
2026-04-06 02:17:04,236 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:17:04,287 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:17:04,289 INFO sqlalchemy.engine.Engine SELECT conversations.id, conversations.user_id, conversations.bucket_id, conversations.title, conversations.web_search_mode, conversations.follow_up_mode, conversations.is_pinned, conversations.created_at, conversations.updated_at 
FROM conversations 
WHERE conversations.id = $1::UUID AND conversations.bucket_id = $2::UUID AND conversations.user_id = $3::UUID
INFO      sqlalchemy.engine.Engine                  SELECT conversations.id, conversations.user_id, conversations.bucket_id, conversations.title, conversations.web_search_mode, conversations.follow_up_mode, conversations.is_pinned, conversations.created_at, conversations.updated_at 
FROM conversations 
WHERE conversations.id = $1::UUID AND conversations.bucket_id = $2::UUID AND conversations.user_id = $3::UUID
2026-04-06 02:17:04,290 INFO sqlalchemy.engine.Engine [cached since 172.8s ago] (UUID('64984f1b-3917-46f0-9555-e0ef067c040b'), UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'), UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'))
INFO      sqlalchemy.engine.Engine                  [cached since 172.8s ago] (UUID('64984f1b-3917-46f0-9555-e0ef067c040b'), UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'), UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'))
2026-04-06 02:17:04,300 INFO sqlalchemy.engine.Engine UPDATE conversations SET title=$1::VARCHAR, updated_at=now() WHERE conversations.id = $2::UUID
INFO      sqlalchemy.engine.Engine                  UPDATE conversations SET title=$1::VARCHAR, updated_at=now() WHERE conversations.id = $2::UUID
2026-04-06 02:17:04,301 INFO sqlalchemy.engine.Engine [generated in 0.00121s] ('Hey read this and let me know hst is in it…', UUID('64984f1b-3917-46f0-9555-e0ef067c040b'))
INFO      sqlalchemy.engine.Engine                  [generated in 0.00121s] ('Hey read this and let me know hst is in it…', UUID('64984f1b-3917-46f0-9555-e0ef067c040b'))
2026-04-06 02:17:04,310 INFO sqlalchemy.engine.Engine INSERT INTO notifications (id, user_id, type, title, message, is_read) VALUES ($1::UUID, $2::UUID, $3::notification_type, $4::VARCHAR, $5::VARCHAR, $6::BOOLEAN) RETURNING notifications.created_at
INFO      sqlalchemy.engine.Engine                  INSERT INTO notifications (id, user_id, type, title, message, is_read) VALUES ($1::UUID, $2::UUID, $3::notification_type, $4::VARCHAR, $5::VARCHAR, $6::BOOLEAN) RETURNING notifications.created_at
2026-04-06 02:17:04,310 INFO sqlalchemy.engine.Engine [cached since 183.9s ago] (UUID('d6b2ab6e-7fd7-4dd7-aa13-aba89d6e9383'), UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), 'info', 'Conversation renamed', 'Conversation renamed to "Hey read this and let me know hst is in it…".', False)
INFO      sqlalchemy.engine.Engine                  [cached since 183.9s ago] (UUID('d6b2ab6e-7fd7-4dd7-aa13-aba89d6e9383'), UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), 'info', 'Conversation renamed', 'Conversation renamed to "Hey read this and let me know hst is in it…".', False)
2026-04-06 02:17:04,313 INFO sqlalchemy.engine.Engine COMMIT
INFO      sqlalchemy.engine.Engine                  COMMIT
2026-04-06 02:17:04,320 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:17:04,321 INFO sqlalchemy.engine.Engine SELECT conversations.id, conversations.user_id, conversations.bucket_id, conversations.title, conversations.web_search_mode, conversations.follow_up_mode, conversations.is_pinned, conversations.created_at, conversations.updated_at 
FROM conversations 
WHERE conversations.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT conversations.id, conversations.user_id, conversations.bucket_id, conversations.title, conversations.web_search_mode, conversations.follow_up_mode, conversations.is_pinned, conversations.created_at, conversations.updated_at 
FROM conversations 
WHERE conversations.id = $1::UUID
2026-04-06 02:17:04,321 INFO sqlalchemy.engine.Engine [cached since 172.9s ago] (UUID('64984f1b-3917-46f0-9555-e0ef067c040b'),)
INFO      sqlalchemy.engine.Engine                  [cached since 172.9s ago] (UUID('64984f1b-3917-46f0-9555-e0ef067c040b'),)
2026-04-06 02:17:04,324 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:17:07,460 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:17:07,462 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:17:07,463 INFO sqlalchemy.engine.Engine [cached since 176.3s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 176.3s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:17:07,466 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
2026-04-06 02:17:07,467 INFO sqlalchemy.engine.Engine [cached since 176.2s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 176.2s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:17:07,470 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
Inference Embeddings:   0%|                                                                                | 0/205 [00:00<?, ?it/s]2026-04-06 02:17:11,506 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:17:11,507 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:17:11,507 INFO sqlalchemy.engine.Engine [cached since 180.3s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 180.3s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:17:11,510 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
2026-04-06 02:17:11,511 INFO sqlalchemy.engine.Engine [cached since 180.3s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 180.3s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:17:11,513 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:17:15,547 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:17:15,547 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:17:15,548 INFO sqlalchemy.engine.Engine [cached since 184.3s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 184.3s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:17:15,551 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
2026-04-06 02:17:15,552 INFO sqlalchemy.engine.Engine [cached since 184.3s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 184.3s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:17:15,554 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:17:19,589 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:17:19,591 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:17:19,591 INFO sqlalchemy.engine.Engine [cached since 188.4s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 188.4s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:17:19,596 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
2026-04-06 02:17:19,597 INFO sqlalchemy.engine.Engine [cached since 188.4s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 188.4s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:17:19,600 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:17:23,633 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:17:23,634 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:17:23,634 INFO sqlalchemy.engine.Engine [cached since 192.4s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 192.4s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:17:23,638 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
2026-04-06 02:17:23,639 INFO sqlalchemy.engine.Engine [cached since 192.4s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 192.4s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:17:23,642 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:17:27,679 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:17:27,680 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:17:27,680 INFO sqlalchemy.engine.Engine [cached since 196.5s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 196.5s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:17:27,683 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
2026-04-06 02:17:27,684 INFO sqlalchemy.engine.Engine [cached since 196.5s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 196.5s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:17:27,687 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:17:31,723 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:17:31,724 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:17:31,725 INFO sqlalchemy.engine.Engine [cached since 200.5s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 200.5s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:17:31,728 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
2026-04-06 02:17:31,728 INFO sqlalchemy.engine.Engine [cached since 200.5s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 200.5s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:17:31,730 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:17:36,273 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:17:36,274 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:17:36,275 INFO sqlalchemy.engine.Engine [cached since 205.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 205.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:17:36,279 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
2026-04-06 02:17:36,280 INFO sqlalchemy.engine.Engine [cached since 205.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 205.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:17:36,283 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:17:41,276 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:17:41,277 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:17:41,278 INFO sqlalchemy.engine.Engine [cached since 210.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 210.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:17:41,281 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
2026-04-06 02:17:41,281 INFO sqlalchemy.engine.Engine [cached since 210.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 210.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:17:41,284 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:17:46,272 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:17:46,273 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:17:46,273 INFO sqlalchemy.engine.Engine [cached since 215.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 215.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:17:46,277 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
2026-04-06 02:17:46,278 INFO sqlalchemy.engine.Engine [cached since 215.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 215.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:17:46,280 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:17:51,273 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:17:51,274 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:17:51,274 INFO sqlalchemy.engine.Engine [cached since 220.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 220.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:17:51,278 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
2026-04-06 02:17:51,279 INFO sqlalchemy.engine.Engine [cached since 220.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 220.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:17:51,282 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:17:56,275 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:17:56,276 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:17:56,277 INFO sqlalchemy.engine.Engine [cached since 225.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 225.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:17:56,280 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
2026-04-06 02:17:56,281 INFO sqlalchemy.engine.Engine [cached since 225.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 225.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:17:56,284 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:18:01,272 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:18:01,273 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:18:01,273 INFO sqlalchemy.engine.Engine [cached since 230.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 230.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:18:01,277 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
2026-04-06 02:18:01,278 INFO sqlalchemy.engine.Engine [cached since 230.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 230.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:18:01,280 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:18:06,271 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:18:06,272 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:18:06,272 INFO sqlalchemy.engine.Engine [cached since 235.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 235.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:18:06,276 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
2026-04-06 02:18:06,276 INFO sqlalchemy.engine.Engine [cached since 235.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 235.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:18:06,279 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:18:11,271 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:18:11,272 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:18:11,272 INFO sqlalchemy.engine.Engine [cached since 240.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 240.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:18:11,276 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
2026-04-06 02:18:11,277 INFO sqlalchemy.engine.Engine [cached since 240.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 240.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:18:11,279 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:18:16,269 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:18:16,271 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:18:16,271 INFO sqlalchemy.engine.Engine [cached since 245.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 245.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:18:16,274 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
2026-04-06 02:18:16,275 INFO sqlalchemy.engine.Engine [cached since 245s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 245s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:18:16,277 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:18:21,274 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:18:21,275 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:18:21,275 INFO sqlalchemy.engine.Engine [cached since 250.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 250.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:18:21,278 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
2026-04-06 02:18:21,279 INFO sqlalchemy.engine.Engine [cached since 250.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 250.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:18:21,281 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:18:26,273 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:18:26,274 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:18:26,275 INFO sqlalchemy.engine.Engine [cached since 255.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 255.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:18:26,279 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
2026-04-06 02:18:26,280 INFO sqlalchemy.engine.Engine [cached since 255.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 255.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:18:26,283 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:18:31,271 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:18:31,272 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:18:31,272 INFO sqlalchemy.engine.Engine [cached since 260.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 260.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:18:31,277 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
2026-04-06 02:18:31,278 INFO sqlalchemy.engine.Engine [cached since 260.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 260.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:18:31,281 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:18:36,272 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:18:36,273 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:18:36,274 INFO sqlalchemy.engine.Engine [cached since 265.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 265.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:18:36,277 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
2026-04-06 02:18:36,278 INFO sqlalchemy.engine.Engine [cached since 265.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 265.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:18:36,280 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:18:41,276 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:18:41,277 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:18:41,278 INFO sqlalchemy.engine.Engine [cached since 270.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 270.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:18:41,281 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
2026-04-06 02:18:41,282 INFO sqlalchemy.engine.Engine [cached since 270.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 270.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:18:41,285 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:18:46,274 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:18:46,276 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:18:46,276 INFO sqlalchemy.engine.Engine [cached since 275.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 275.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:18:46,280 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
2026-04-06 02:18:46,281 INFO sqlalchemy.engine.Engine [cached since 275.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 275.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:18:46,283 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:18:51,270 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:18:51,271 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:18:51,271 INFO sqlalchemy.engine.Engine [cached since 280.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 280.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:18:51,275 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
2026-04-06 02:18:51,276 INFO sqlalchemy.engine.Engine [cached since 280s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 280s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:18:51,278 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:18:56,271 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:18:56,272 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:18:56,272 INFO sqlalchemy.engine.Engine [cached since 285.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 285.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:18:56,275 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
2026-04-06 02:18:56,276 INFO sqlalchemy.engine.Engine [cached since 285s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 285s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:18:56,278 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:19:01,269 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:19:01,271 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:19:01,273 INFO sqlalchemy.engine.Engine [cached since 290.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 290.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:19:01,276 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
2026-04-06 02:19:01,277 INFO sqlalchemy.engine.Engine [cached since 290.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 290.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:19:01,280 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:19:06,443 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:19:06,447 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:19:06,447 INFO sqlalchemy.engine.Engine [cached since 295.2s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 295.2s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:19:06,455 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
2026-04-06 02:19:06,459 INFO sqlalchemy.engine.Engine [cached since 295.2s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 295.2s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:19:06,463 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:19:11,063 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:19:11,191 INFO sqlalchemy.engine.Engine SELECT users.id, users.email, users.password_hash, users.provider, users.provider_id, users.is_verified, users.is_active, users.two_factor_enabled, users.two_factor_secret, users.two_factor_backup_codes, users.created_at, users.updated_at 
FROM users 
WHERE users.email = $1::VARCHAR
INFO      sqlalchemy.engine.Engine                  SELECT users.id, users.email, users.password_hash, users.provider, users.provider_id, users.is_verified, users.is_active, users.two_factor_enabled, users.two_factor_secret, users.two_factor_backup_codes, users.created_at, users.updated_at 
FROM users 
WHERE users.email = $1::VARCHAR
2026-04-06 02:19:11,192 INFO sqlalchemy.engine.Engine [cached since 311.3s ago] ('chaffanjutt313@gmail.com',)
INFO      sqlalchemy.engine.Engine                  [cached since 311.3s ago] ('chaffanjutt313@gmail.com',)
2026-04-06 02:19:11,511 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:19:11,516 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:19:11,516 INFO sqlalchemy.engine.Engine [cached since 300.3s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 300.3s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:19:11,522 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
2026-04-06 02:19:11,526 INFO sqlalchemy.engine.Engine [cached since 300.3s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 300.3s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:19:11,529 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:19:12,496 INFO sqlalchemy.engine.Engine INSERT INTO notifications (id, user_id, type, title, message, is_read) VALUES ($1::UUID, $2::UUID, $3::notification_type, $4::VARCHAR, $5::VARCHAR, $6::BOOLEAN) RETURNING notifications.created_at
INFO      sqlalchemy.engine.Engine                  INSERT INTO notifications (id, user_id, type, title, message, is_read) VALUES ($1::UUID, $2::UUID, $3::notification_type, $4::VARCHAR, $5::VARCHAR, $6::BOOLEAN) RETURNING notifications.created_at
2026-04-06 02:19:12,497 INFO sqlalchemy.engine.Engine [cached since 312.1s ago] (UUID('3f6c8e13-b52b-47af-a393-8eeea9075243'), UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), 'info', 'Signed in', 'You signed in to your AIveilix account.', False)
INFO      sqlalchemy.engine.Engine                  [cached since 312.1s ago] (UUID('3f6c8e13-b52b-47af-a393-8eeea9075243'), UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), 'info', 'Signed in', 'You signed in to your AIveilix account.', False)
2026-04-06 02:19:12,499 INFO sqlalchemy.engine.Engine COMMIT
INFO      sqlalchemy.engine.Engine                  COMMIT
2026-04-06 02:19:12,519 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:19:12,520 INFO sqlalchemy.engine.Engine SELECT notifications.id, notifications.user_id, notifications.type, notifications.title, notifications.message, notifications.is_read, notifications.created_at 
FROM notifications 
WHERE notifications.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT notifications.id, notifications.user_id, notifications.type, notifications.title, notifications.message, notifications.is_read, notifications.created_at 
FROM notifications 
WHERE notifications.id = $1::UUID
2026-04-06 02:19:12,521 INFO sqlalchemy.engine.Engine [cached since 312.1s ago] (UUID('3f6c8e13-b52b-47af-a393-8eeea9075243'),)
INFO      sqlalchemy.engine.Engine                  [cached since 312.1s ago] (UUID('3f6c8e13-b52b-47af-a393-8eeea9075243'),)
2026-04-06 02:19:12,553 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:19:12,701 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:19:12,702 INFO sqlalchemy.engine.Engine SELECT coalesce(sum(files.size), $1::INTEGER) AS coalesce_1, count(files.id) AS count_1 
FROM files JOIN buckets ON files.bucket_id = buckets.id 
WHERE buckets.user_id = $2::UUID
INFO      sqlalchemy.engine.Engine                  SELECT coalesce(sum(files.size), $1::INTEGER) AS coalesce_1, count(files.id) AS count_1 
FROM files JOIN buckets ON files.bucket_id = buckets.id 
WHERE buckets.user_id = $2::UUID
2026-04-06 02:19:12,703 INFO sqlalchemy.engine.Engine [cached since 311.9s ago] (0, UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'))
INFO      sqlalchemy.engine.Engine                  [cached since 311.9s ago] (0, UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'))
2026-04-06 02:19:12,704 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:19:12,705 INFO sqlalchemy.engine.Engine SELECT users.id, users.email, users.password_hash, users.provider, users.provider_id, users.is_verified, users.is_active, users.two_factor_enabled, users.two_factor_secret, users.two_factor_backup_codes, users.created_at, users.updated_at 
FROM users 
WHERE users.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT users.id, users.email, users.password_hash, users.provider, users.provider_id, users.is_verified, users.is_active, users.two_factor_enabled, users.two_factor_secret, users.two_factor_backup_codes, users.created_at, users.updated_at 
FROM users 
WHERE users.id = $1::UUID
2026-04-06 02:19:12,705 INFO sqlalchemy.engine.Engine [cached since 312.1s ago] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'),)
INFO      sqlalchemy.engine.Engine                  [cached since 312.1s ago] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'),)
2026-04-06 02:19:12,732 INFO sqlalchemy.engine.Engine SELECT count(*) AS count_1 
FROM buckets 
WHERE buckets.user_id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT count(*) AS count_1 
FROM buckets 
WHERE buckets.user_id = $1::UUID
2026-04-06 02:19:12,733 INFO sqlalchemy.engine.Engine [cached since 311.9s ago] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'),)
INFO      sqlalchemy.engine.Engine                  [cached since 311.9s ago] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'),)
2026-04-06 02:19:12,735 INFO sqlalchemy.engine.Engine SELECT profiles.id, profiles.user_id, profiles.full_name, profiles.avatar_url, profiles.bio, profiles.theme, profiles.language, profiles.timezone, profiles.preferred_llm, profiles.follow_up_mode, profiles.use_case, profiles.referral_source, profiles.updated_at 
FROM profiles 
WHERE profiles.user_id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT profiles.id, profiles.user_id, profiles.full_name, profiles.avatar_url, profiles.bio, profiles.theme, profiles.language, profiles.timezone, profiles.preferred_llm, profiles.follow_up_mode, profiles.use_case, profiles.referral_source, profiles.updated_at 
FROM profiles 
WHERE profiles.user_id = $1::UUID
2026-04-06 02:19:12,736 INFO sqlalchemy.engine.Engine [cached since 312.1s ago] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'),)
INFO      sqlalchemy.engine.Engine                  [cached since 312.1s ago] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'),)
2026-04-06 02:19:12,743 INFO sqlalchemy.engine.Engine SELECT oauth_tokens.provider 
FROM oauth_tokens 
WHERE oauth_tokens.user_id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT oauth_tokens.provider 
FROM oauth_tokens 
WHERE oauth_tokens.user_id = $1::UUID
2026-04-06 02:19:12,744 INFO sqlalchemy.engine.Engine [cached since 311.9s ago] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'),)
INFO      sqlalchemy.engine.Engine                  [cached since 311.9s ago] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'),)
2026-04-06 02:19:12,747 INFO sqlalchemy.engine.Engine SELECT count(messages.id) AS count_1 
FROM messages JOIN conversations ON messages.conversation_id = conversations.id 
WHERE conversations.user_id = $1::UUID AND messages.created_at >= $2::DATE
INFO      sqlalchemy.engine.Engine                  SELECT count(messages.id) AS count_1 
FROM messages JOIN conversations ON messages.conversation_id = conversations.id 
WHERE conversations.user_id = $1::UUID AND messages.created_at >= $2::DATE
2026-04-06 02:19:12,748 INFO sqlalchemy.engine.Engine [cached since 311.9s ago] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), datetime.date(2026, 4, 1))
INFO      sqlalchemy.engine.Engine                  [cached since 311.9s ago] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), datetime.date(2026, 4, 1))
2026-04-06 02:19:12,774 INFO sqlalchemy.engine.Engine COMMIT
INFO      sqlalchemy.engine.Engine                  COMMIT
2026-04-06 02:19:12,776 INFO sqlalchemy.engine.Engine SELECT usage_tracking.id, usage_tracking.user_id, usage_tracking.month, usage_tracking.storage_used, usage_tracking.chat_messages_count, usage_tracking.mcp_calls_count, usage_tracking.buckets_count, usage_tracking.files_count, usage_tracking.updated_at 
FROM usage_tracking 
WHERE usage_tracking.user_id = $1::UUID AND usage_tracking.month = $2::DATE
INFO      sqlalchemy.engine.Engine                  SELECT usage_tracking.id, usage_tracking.user_id, usage_tracking.month, usage_tracking.storage_used, usage_tracking.chat_messages_count, usage_tracking.mcp_calls_count, usage_tracking.buckets_count, usage_tracking.files_count, usage_tracking.updated_at 
FROM usage_tracking 
WHERE usage_tracking.user_id = $1::UUID AND usage_tracking.month = $2::DATE
2026-04-06 02:19:12,777 INFO sqlalchemy.engine.Engine [cached since 311.9s ago] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), datetime.date(2026, 4, 1))
INFO      sqlalchemy.engine.Engine                  [cached since 311.9s ago] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), datetime.date(2026, 4, 1))
2026-04-06 02:19:12,784 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:19:12,944 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:19:12,945 INFO sqlalchemy.engine.Engine SELECT count(buckets.id) AS count_1 
FROM buckets 
WHERE buckets.user_id = $1::UUID AND buckets.created_at < $2::DATE
INFO      sqlalchemy.engine.Engine                  SELECT count(buckets.id) AS count_1 
FROM buckets 
WHERE buckets.user_id = $1::UUID AND buckets.created_at < $2::DATE
2026-04-06 02:19:12,945 INFO sqlalchemy.engine.Engine [cached since 312.1s ago] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), datetime.date(2025, 11, 1))
INFO      sqlalchemy.engine.Engine                  [cached since 312.1s ago] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), datetime.date(2025, 11, 1))
2026-04-06 02:19:12,955 INFO sqlalchemy.engine.Engine SELECT count(files.id) AS count_1, coalesce(sum(files.size), $1::INTEGER) AS coalesce_1 
FROM files JOIN buckets ON files.bucket_id = buckets.id 
WHERE buckets.user_id = $2::UUID AND files.created_at < $3::DATE
INFO      sqlalchemy.engine.Engine                  SELECT count(files.id) AS count_1, coalesce(sum(files.size), $1::INTEGER) AS coalesce_1 
FROM files JOIN buckets ON files.bucket_id = buckets.id 
WHERE buckets.user_id = $2::UUID AND files.created_at < $3::DATE
2026-04-06 02:19:12,956 INFO sqlalchemy.engine.Engine [cached since 312.1s ago] (0, UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), datetime.date(2025, 11, 1))
INFO      sqlalchemy.engine.Engine                  [cached since 312.1s ago] (0, UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), datetime.date(2025, 11, 1))
2026-04-06 02:19:12,958 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:19:12,959 INFO sqlalchemy.engine.Engine SELECT buckets.id, buckets.user_id, buckets.name, buckets.description, buckets.mcp_url, buckets.mcp_token, buckets.account_mcp_url, buckets.account_mcp_token, buckets.color, buckets.icon, buckets.is_public, buckets.storage_used, buckets.created_at, buckets.updated_at 
FROM buckets 
WHERE buckets.user_id = $1::UUID ORDER BY buckets.updated_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id, buckets.user_id, buckets.name, buckets.description, buckets.mcp_url, buckets.mcp_token, buckets.account_mcp_url, buckets.account_mcp_token, buckets.color, buckets.icon, buckets.is_public, buckets.storage_used, buckets.created_at, buckets.updated_at 
FROM buckets 
WHERE buckets.user_id = $1::UUID ORDER BY buckets.updated_at DESC
2026-04-06 02:19:12,960 INFO sqlalchemy.engine.Engine [cached since 312.1s ago] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'),)
INFO      sqlalchemy.engine.Engine                  [cached since 312.1s ago] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'),)
2026-04-06 02:19:12,967 INFO sqlalchemy.engine.Engine SELECT date_trunc($1::VARCHAR, buckets.created_at) AS bucket_month, count(buckets.id) AS count_1 
FROM buckets 
WHERE buckets.user_id = $2::UUID AND buckets.created_at >= $3::DATE AND buckets.created_at < $4::DATE GROUP BY date_trunc($1::VARCHAR, buckets.created_at) ORDER BY bucket_month ASC
INFO      sqlalchemy.engine.Engine                  SELECT date_trunc($1::VARCHAR, buckets.created_at) AS bucket_month, count(buckets.id) AS count_1 
FROM buckets 
WHERE buckets.user_id = $2::UUID AND buckets.created_at >= $3::DATE AND buckets.created_at < $4::DATE GROUP BY date_trunc($1::VARCHAR, buckets.created_at) ORDER BY bucket_month ASC
2026-04-06 02:19:12,968 INFO sqlalchemy.engine.Engine [cached since 312.1s ago] ('month', UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), datetime.date(2025, 11, 1), datetime.date(2026, 5, 1))
INFO      sqlalchemy.engine.Engine                  [cached since 312.1s ago] ('month', UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), datetime.date(2025, 11, 1), datetime.date(2026, 5, 1))
2026-04-06 02:19:12,983 INFO sqlalchemy.engine.Engine SELECT date_trunc($1::VARCHAR, files.created_at) AS file_month, count(files.id) AS count_1, coalesce(sum(files.size), $2::INTEGER) AS coalesce_1 
FROM files JOIN buckets ON files.bucket_id = buckets.id 
WHERE buckets.user_id = $3::UUID AND files.created_at >= $4::DATE AND files.created_at < $5::DATE GROUP BY date_trunc($1::VARCHAR, files.created_at) ORDER BY file_month ASC
INFO      sqlalchemy.engine.Engine                  SELECT date_trunc($1::VARCHAR, files.created_at) AS file_month, count(files.id) AS count_1, coalesce(sum(files.size), $2::INTEGER) AS coalesce_1 
FROM files JOIN buckets ON files.bucket_id = buckets.id 
WHERE buckets.user_id = $3::UUID AND files.created_at >= $4::DATE AND files.created_at < $5::DATE GROUP BY date_trunc($1::VARCHAR, files.created_at) ORDER BY file_month ASC
2026-04-06 02:19:12,984 INFO sqlalchemy.engine.Engine [cached since 311.7s ago] ('month', 0, UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), datetime.date(2025, 11, 1), datetime.date(2026, 5, 1))
INFO      sqlalchemy.engine.Engine                  [cached since 311.7s ago] ('month', 0, UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), datetime.date(2025, 11, 1), datetime.date(2026, 5, 1))
2026-04-06 02:19:13,227 INFO sqlalchemy.engine.Engine SELECT files.bucket_id, count(files.id) AS count_1, coalesce(sum(files.size), $1::INTEGER) AS coalesce_1 
FROM files 
WHERE files.bucket_id IN ($2::UUID, $3::UUID, $4::UUID) GROUP BY files.bucket_id
INFO      sqlalchemy.engine.Engine                  SELECT files.bucket_id, count(files.id) AS count_1, coalesce(sum(files.size), $1::INTEGER) AS coalesce_1 
FROM files 
WHERE files.bucket_id IN ($2::UUID, $3::UUID, $4::UUID) GROUP BY files.bucket_id
2026-04-06 02:19:13,227 INFO sqlalchemy.engine.Engine [cached since 312.4s ago] (0, UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'), UUID('fe09f04f-d026-46bb-ba04-67d06a415573'), UUID('083d9deb-aab6-48e9-9e73-80c4f63676d5'))
INFO      sqlalchemy.engine.Engine                  [cached since 312.4s ago] (0, UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'), UUID('fe09f04f-d026-46bb-ba04-67d06a415573'), UUID('083d9deb-aab6-48e9-9e73-80c4f63676d5'))
2026-04-06 02:19:13,230 INFO sqlalchemy.engine.Engine SELECT date_trunc($1::VARCHAR, messages.created_at) AS message_month, count(messages.id) AS count_1 
FROM messages JOIN conversations ON messages.conversation_id = conversations.id 
WHERE conversations.user_id = $2::UUID AND messages.created_at >= $3::DATE AND messages.created_at < $4::DATE GROUP BY date_trunc($1::VARCHAR, messages.created_at) ORDER BY message_month ASC
INFO      sqlalchemy.engine.Engine                  SELECT date_trunc($1::VARCHAR, messages.created_at) AS message_month, count(messages.id) AS count_1 
FROM messages JOIN conversations ON messages.conversation_id = conversations.id 
WHERE conversations.user_id = $2::UUID AND messages.created_at >= $3::DATE AND messages.created_at < $4::DATE GROUP BY date_trunc($1::VARCHAR, messages.created_at) ORDER BY message_month ASC
2026-04-06 02:19:13,231 INFO sqlalchemy.engine.Engine [cached since 312s ago] ('month', UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), datetime.date(2025, 11, 1), datetime.date(2026, 5, 1))
INFO      sqlalchemy.engine.Engine                  [cached since 312s ago] ('month', UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), datetime.date(2025, 11, 1), datetime.date(2026, 5, 1))
2026-04-06 02:19:13,234 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:19:13,237 INFO sqlalchemy.engine.Engine SELECT users.id, users.email, users.password_hash, users.provider, users.provider_id, users.is_verified, users.is_active, users.two_factor_enabled, users.two_factor_secret, users.two_factor_backup_codes, users.created_at, users.updated_at 
FROM users 
WHERE users.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT users.id, users.email, users.password_hash, users.provider, users.provider_id, users.is_verified, users.is_active, users.two_factor_enabled, users.two_factor_secret, users.two_factor_backup_codes, users.created_at, users.updated_at 
FROM users 
WHERE users.id = $1::UUID
2026-04-06 02:19:13,237 INFO sqlalchemy.engine.Engine [cached since 312.6s ago] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'),)
INFO      sqlalchemy.engine.Engine                  [cached since 312.6s ago] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'),)
2026-04-06 02:19:13,239 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:19:13,242 INFO sqlalchemy.engine.Engine SELECT coalesce(sum(files.size), $1::INTEGER) AS coalesce_1, count(files.id) AS count_1 
FROM files JOIN buckets ON files.bucket_id = buckets.id 
WHERE buckets.user_id = $2::UUID
INFO      sqlalchemy.engine.Engine                  SELECT coalesce(sum(files.size), $1::INTEGER) AS coalesce_1, count(files.id) AS count_1 
FROM files JOIN buckets ON files.bucket_id = buckets.id 
WHERE buckets.user_id = $2::UUID
2026-04-06 02:19:13,242 INFO sqlalchemy.engine.Engine [cached since 312.4s ago] (0, UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'))
INFO      sqlalchemy.engine.Engine                  [cached since 312.4s ago] (0, UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'))
2026-04-06 02:19:13,246 INFO sqlalchemy.engine.Engine SELECT usage_tracking.month, usage_tracking.mcp_calls_count 
FROM usage_tracking 
WHERE usage_tracking.user_id = $1::UUID AND usage_tracking.month >= $2::DATE AND usage_tracking.month <= $3::DATE ORDER BY usage_tracking.month ASC
INFO      sqlalchemy.engine.Engine                  SELECT usage_tracking.month, usage_tracking.mcp_calls_count 
FROM usage_tracking 
WHERE usage_tracking.user_id = $1::UUID AND usage_tracking.month >= $2::DATE AND usage_tracking.month <= $3::DATE ORDER BY usage_tracking.month ASC
2026-04-06 02:19:13,247 INFO sqlalchemy.engine.Engine [cached since 312s ago] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), datetime.date(2025, 11, 1), datetime.date(2026, 4, 1))
INFO      sqlalchemy.engine.Engine                  [cached since 312s ago] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), datetime.date(2025, 11, 1), datetime.date(2026, 4, 1))
2026-04-06 02:19:13,251 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:19:13,253 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:19:13,254 INFO sqlalchemy.engine.Engine SELECT notifications.id, notifications.user_id, notifications.type, notifications.title, notifications.message, notifications.is_read, notifications.created_at 
FROM notifications 
WHERE notifications.user_id = $1::UUID ORDER BY notifications.created_at DESC 
 LIMIT $2::INTEGER
INFO      sqlalchemy.engine.Engine                  SELECT notifications.id, notifications.user_id, notifications.type, notifications.title, notifications.message, notifications.is_read, notifications.created_at 
FROM notifications 
WHERE notifications.user_id = $1::UUID ORDER BY notifications.created_at DESC 
 LIMIT $2::INTEGER
2026-04-06 02:19:13,254 INFO sqlalchemy.engine.Engine [cached since 312.4s ago] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), 20)
INFO      sqlalchemy.engine.Engine                  [cached since 312.4s ago] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), 20)
2026-04-06 02:19:13,258 INFO sqlalchemy.engine.Engine SELECT count(*) AS count_1 
FROM buckets 
WHERE buckets.user_id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT count(*) AS count_1 
FROM buckets 
WHERE buckets.user_id = $1::UUID
2026-04-06 02:19:13,258 INFO sqlalchemy.engine.Engine [cached since 312.4s ago] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'),)
INFO      sqlalchemy.engine.Engine                  [cached since 312.4s ago] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'),)
2026-04-06 02:19:13,264 INFO sqlalchemy.engine.Engine SELECT count(messages.id) AS count_1 
FROM messages JOIN conversations ON messages.conversation_id = conversations.id 
WHERE conversations.user_id = $1::UUID AND messages.created_at >= $2::DATE
INFO      sqlalchemy.engine.Engine                  SELECT count(messages.id) AS count_1 
FROM messages JOIN conversations ON messages.conversation_id = conversations.id 
WHERE conversations.user_id = $1::UUID AND messages.created_at >= $2::DATE
2026-04-06 02:19:13,265 INFO sqlalchemy.engine.Engine [cached since 312.4s ago] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), datetime.date(2026, 4, 1))
INFO      sqlalchemy.engine.Engine                  [cached since 312.4s ago] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), datetime.date(2026, 4, 1))
2026-04-06 02:19:13,269 INFO sqlalchemy.engine.Engine SELECT usage_tracking.id, usage_tracking.user_id, usage_tracking.month, usage_tracking.storage_used, usage_tracking.chat_messages_count, usage_tracking.mcp_calls_count, usage_tracking.buckets_count, usage_tracking.files_count, usage_tracking.updated_at 
FROM usage_tracking 
WHERE usage_tracking.user_id = $1::UUID AND usage_tracking.month = $2::DATE
INFO      sqlalchemy.engine.Engine                  SELECT usage_tracking.id, usage_tracking.user_id, usage_tracking.month, usage_tracking.storage_used, usage_tracking.chat_messages_count, usage_tracking.mcp_calls_count, usage_tracking.buckets_count, usage_tracking.files_count, usage_tracking.updated_at 
FROM usage_tracking 
WHERE usage_tracking.user_id = $1::UUID AND usage_tracking.month = $2::DATE
2026-04-06 02:19:13,271 INFO sqlalchemy.engine.Engine [cached since 312.4s ago] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), datetime.date(2026, 4, 1))
INFO      sqlalchemy.engine.Engine                  [cached since 312.4s ago] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), datetime.date(2026, 4, 1))
2026-04-06 02:19:13,278 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:19:13,287 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:19:13,300 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:19:13,302 INFO sqlalchemy.engine.Engine SELECT buckets.id, buckets.user_id, buckets.name, buckets.description, buckets.mcp_url, buckets.mcp_token, buckets.account_mcp_url, buckets.account_mcp_token, buckets.color, buckets.icon, buckets.is_public, buckets.storage_used, buckets.created_at, buckets.updated_at 
FROM buckets 
WHERE buckets.user_id = $1::UUID ORDER BY buckets.updated_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id, buckets.user_id, buckets.name, buckets.description, buckets.mcp_url, buckets.mcp_token, buckets.account_mcp_url, buckets.account_mcp_token, buckets.color, buckets.icon, buckets.is_public, buckets.storage_used, buckets.created_at, buckets.updated_at 
FROM buckets 
WHERE buckets.user_id = $1::UUID ORDER BY buckets.updated_at DESC
2026-04-06 02:19:13,305 INFO sqlalchemy.engine.Engine [cached since 312.5s ago] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'),)
INFO      sqlalchemy.engine.Engine                  [cached since 312.5s ago] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'),)
2026-04-06 02:19:13,310 INFO sqlalchemy.engine.Engine SELECT profiles.id, profiles.user_id, profiles.full_name, profiles.avatar_url, profiles.bio, profiles.theme, profiles.language, profiles.timezone, profiles.preferred_llm, profiles.follow_up_mode, profiles.use_case, profiles.referral_source, profiles.updated_at 
FROM profiles 
WHERE profiles.user_id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT profiles.id, profiles.user_id, profiles.full_name, profiles.avatar_url, profiles.bio, profiles.theme, profiles.language, profiles.timezone, profiles.preferred_llm, profiles.follow_up_mode, profiles.use_case, profiles.referral_source, profiles.updated_at 
FROM profiles 
WHERE profiles.user_id = $1::UUID
2026-04-06 02:19:13,314 INFO sqlalchemy.engine.Engine [cached since 312.7s ago] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'),)
INFO      sqlalchemy.engine.Engine                  [cached since 312.7s ago] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'),)
2026-04-06 02:19:13,445 INFO sqlalchemy.engine.Engine SELECT oauth_tokens.provider 
FROM oauth_tokens 
WHERE oauth_tokens.user_id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT oauth_tokens.provider 
FROM oauth_tokens 
WHERE oauth_tokens.user_id = $1::UUID
2026-04-06 02:19:13,446 INFO sqlalchemy.engine.Engine [cached since 312.6s ago] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'),)
INFO      sqlalchemy.engine.Engine                  [cached since 312.6s ago] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'),)
2026-04-06 02:19:13,455 INFO sqlalchemy.engine.Engine SELECT files.bucket_id, count(files.id) AS count_1, coalesce(sum(files.size), $1::INTEGER) AS coalesce_1 
FROM files 
WHERE files.bucket_id IN ($2::UUID, $3::UUID, $4::UUID) GROUP BY files.bucket_id
INFO      sqlalchemy.engine.Engine                  SELECT files.bucket_id, count(files.id) AS count_1, coalesce(sum(files.size), $1::INTEGER) AS coalesce_1 
FROM files 
WHERE files.bucket_id IN ($2::UUID, $3::UUID, $4::UUID) GROUP BY files.bucket_id
2026-04-06 02:19:13,456 INFO sqlalchemy.engine.Engine [cached since 312.6s ago] (0, UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'), UUID('fe09f04f-d026-46bb-ba04-67d06a415573'), UUID('083d9deb-aab6-48e9-9e73-80c4f63676d5'))
INFO      sqlalchemy.engine.Engine                  [cached since 312.6s ago] (0, UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'), UUID('fe09f04f-d026-46bb-ba04-67d06a415573'), UUID('083d9deb-aab6-48e9-9e73-80c4f63676d5'))
2026-04-06 02:19:13,461 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:19:13,464 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:19:13,465 INFO sqlalchemy.engine.Engine SELECT count(buckets.id) AS count_1 
FROM buckets 
WHERE buckets.user_id = $1::UUID AND buckets.created_at < $2::DATE
INFO      sqlalchemy.engine.Engine                  SELECT count(buckets.id) AS count_1 
FROM buckets 
WHERE buckets.user_id = $1::UUID AND buckets.created_at < $2::DATE
2026-04-06 02:19:13,465 INFO sqlalchemy.engine.Engine [cached since 312.6s ago] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), datetime.date(2025, 11, 1))
INFO      sqlalchemy.engine.Engine                  [cached since 312.6s ago] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), datetime.date(2025, 11, 1))
2026-04-06 02:19:13,467 INFO sqlalchemy.engine.Engine COMMIT
INFO      sqlalchemy.engine.Engine                  COMMIT
2026-04-06 02:19:13,469 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:19:13,473 INFO sqlalchemy.engine.Engine SELECT count(files.id) AS count_1, coalesce(sum(files.size), $1::INTEGER) AS coalesce_1 
FROM files JOIN buckets ON files.bucket_id = buckets.id 
WHERE buckets.user_id = $2::UUID AND files.created_at < $3::DATE
INFO      sqlalchemy.engine.Engine                  SELECT count(files.id) AS count_1, coalesce(sum(files.size), $1::INTEGER) AS coalesce_1 
FROM files JOIN buckets ON files.bucket_id = buckets.id 
WHERE buckets.user_id = $2::UUID AND files.created_at < $3::DATE
2026-04-06 02:19:13,474 INFO sqlalchemy.engine.Engine [cached since 312.6s ago] (0, UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), datetime.date(2025, 11, 1))
INFO      sqlalchemy.engine.Engine                  [cached since 312.6s ago] (0, UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), datetime.date(2025, 11, 1))
2026-04-06 02:19:13,479 INFO sqlalchemy.engine.Engine SELECT date_trunc($1::VARCHAR, buckets.created_at) AS bucket_month, count(buckets.id) AS count_1 
FROM buckets 
WHERE buckets.user_id = $2::UUID AND buckets.created_at >= $3::DATE AND buckets.created_at < $4::DATE GROUP BY date_trunc($1::VARCHAR, buckets.created_at) ORDER BY bucket_month ASC
INFO      sqlalchemy.engine.Engine                  SELECT date_trunc($1::VARCHAR, buckets.created_at) AS bucket_month, count(buckets.id) AS count_1 
FROM buckets 
WHERE buckets.user_id = $2::UUID AND buckets.created_at >= $3::DATE AND buckets.created_at < $4::DATE GROUP BY date_trunc($1::VARCHAR, buckets.created_at) ORDER BY bucket_month ASC
2026-04-06 02:19:13,480 INFO sqlalchemy.engine.Engine [cached since 312.6s ago] ('month', UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), datetime.date(2025, 11, 1), datetime.date(2026, 5, 1))
INFO      sqlalchemy.engine.Engine                  [cached since 312.6s ago] ('month', UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), datetime.date(2025, 11, 1), datetime.date(2026, 5, 1))
2026-04-06 02:19:13,484 INFO sqlalchemy.engine.Engine SELECT date_trunc($1::VARCHAR, files.created_at) AS file_month, count(files.id) AS count_1, coalesce(sum(files.size), $2::INTEGER) AS coalesce_1 
FROM files JOIN buckets ON files.bucket_id = buckets.id 
WHERE buckets.user_id = $3::UUID AND files.created_at >= $4::DATE AND files.created_at < $5::DATE GROUP BY date_trunc($1::VARCHAR, files.created_at) ORDER BY file_month ASC
INFO      sqlalchemy.engine.Engine                  SELECT date_trunc($1::VARCHAR, files.created_at) AS file_month, count(files.id) AS count_1, coalesce(sum(files.size), $2::INTEGER) AS coalesce_1 
FROM files JOIN buckets ON files.bucket_id = buckets.id 
WHERE buckets.user_id = $3::UUID AND files.created_at >= $4::DATE AND files.created_at < $5::DATE GROUP BY date_trunc($1::VARCHAR, files.created_at) ORDER BY file_month ASC
2026-04-06 02:19:13,485 INFO sqlalchemy.engine.Engine [cached since 312.2s ago] ('month', 0, UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), datetime.date(2025, 11, 1), datetime.date(2026, 5, 1))
INFO      sqlalchemy.engine.Engine                  [cached since 312.2s ago] ('month', 0, UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), datetime.date(2025, 11, 1), datetime.date(2026, 5, 1))
2026-04-06 02:19:13,490 INFO sqlalchemy.engine.Engine SELECT date_trunc($1::VARCHAR, messages.created_at) AS message_month, count(messages.id) AS count_1 
FROM messages JOIN conversations ON messages.conversation_id = conversations.id 
WHERE conversations.user_id = $2::UUID AND messages.created_at >= $3::DATE AND messages.created_at < $4::DATE GROUP BY date_trunc($1::VARCHAR, messages.created_at) ORDER BY message_month ASC
INFO      sqlalchemy.engine.Engine                  SELECT date_trunc($1::VARCHAR, messages.created_at) AS message_month, count(messages.id) AS count_1 
FROM messages JOIN conversations ON messages.conversation_id = conversations.id 
WHERE conversations.user_id = $2::UUID AND messages.created_at >= $3::DATE AND messages.created_at < $4::DATE GROUP BY date_trunc($1::VARCHAR, messages.created_at) ORDER BY message_month ASC
2026-04-06 02:19:13,491 INFO sqlalchemy.engine.Engine [cached since 312.2s ago] ('month', UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), datetime.date(2025, 11, 1), datetime.date(2026, 5, 1))
INFO      sqlalchemy.engine.Engine                  [cached since 312.2s ago] ('month', UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), datetime.date(2025, 11, 1), datetime.date(2026, 5, 1))
2026-04-06 02:19:13,495 INFO sqlalchemy.engine.Engine SELECT usage_tracking.month, usage_tracking.mcp_calls_count 
FROM usage_tracking 
WHERE usage_tracking.user_id = $1::UUID AND usage_tracking.month >= $2::DATE AND usage_tracking.month <= $3::DATE ORDER BY usage_tracking.month ASC
INFO      sqlalchemy.engine.Engine                  SELECT usage_tracking.month, usage_tracking.mcp_calls_count 
FROM usage_tracking 
WHERE usage_tracking.user_id = $1::UUID AND usage_tracking.month >= $2::DATE AND usage_tracking.month <= $3::DATE ORDER BY usage_tracking.month ASC
2026-04-06 02:19:13,495 INFO sqlalchemy.engine.Engine [cached since 312.2s ago] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), datetime.date(2025, 11, 1), datetime.date(2026, 4, 1))
INFO      sqlalchemy.engine.Engine                  [cached since 312.2s ago] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), datetime.date(2025, 11, 1), datetime.date(2026, 4, 1))
2026-04-06 02:19:13,498 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:19:13,505 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:19:13,506 INFO sqlalchemy.engine.Engine SELECT notifications.id, notifications.user_id, notifications.type, notifications.title, notifications.message, notifications.is_read, notifications.created_at 
FROM notifications 
WHERE notifications.user_id = $1::UUID ORDER BY notifications.created_at DESC 
 LIMIT $2::INTEGER
INFO      sqlalchemy.engine.Engine                  SELECT notifications.id, notifications.user_id, notifications.type, notifications.title, notifications.message, notifications.is_read, notifications.created_at 
FROM notifications 
WHERE notifications.user_id = $1::UUID ORDER BY notifications.created_at DESC 
 LIMIT $2::INTEGER
2026-04-06 02:19:13,507 INFO sqlalchemy.engine.Engine [cached since 312.7s ago] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), 20)
INFO      sqlalchemy.engine.Engine                  [cached since 312.7s ago] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'), 20)
2026-04-06 02:19:13,512 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:19:16,273 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:19:16,275 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:19:16,275 INFO sqlalchemy.engine.Engine [cached since 305.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 305.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:19:16,281 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
2026-04-06 02:19:16,282 INFO sqlalchemy.engine.Engine [cached since 305.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 305.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:19:16,298 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:19:19,755 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:19:19,756 INFO sqlalchemy.engine.Engine SELECT buckets.id, buckets.user_id, buckets.name, buckets.description, buckets.mcp_url, buckets.mcp_token, buckets.account_mcp_url, buckets.account_mcp_token, buckets.color, buckets.icon, buckets.is_public, buckets.storage_used, buckets.created_at, buckets.updated_at 
FROM buckets 
WHERE buckets.user_id = $1::UUID ORDER BY buckets.updated_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id, buckets.user_id, buckets.name, buckets.description, buckets.mcp_url, buckets.mcp_token, buckets.account_mcp_url, buckets.account_mcp_token, buckets.color, buckets.icon, buckets.is_public, buckets.storage_used, buckets.created_at, buckets.updated_at 
FROM buckets 
WHERE buckets.user_id = $1::UUID ORDER BY buckets.updated_at DESC
2026-04-06 02:19:19,757 INFO sqlalchemy.engine.Engine [cached since 318.9s ago] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'),)
INFO      sqlalchemy.engine.Engine                  [cached since 318.9s ago] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'),)
2026-04-06 02:19:19,762 INFO sqlalchemy.engine.Engine SELECT files.bucket_id, count(files.id) AS count_1, coalesce(sum(files.size), $1::INTEGER) AS coalesce_1 
FROM files 
WHERE files.bucket_id IN ($2::UUID, $3::UUID, $4::UUID) GROUP BY files.bucket_id
INFO      sqlalchemy.engine.Engine                  SELECT files.bucket_id, count(files.id) AS count_1, coalesce(sum(files.size), $1::INTEGER) AS coalesce_1 
FROM files 
WHERE files.bucket_id IN ($2::UUID, $3::UUID, $4::UUID) GROUP BY files.bucket_id
2026-04-06 02:19:19,763 INFO sqlalchemy.engine.Engine [cached since 318.9s ago] (0, UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'), UUID('fe09f04f-d026-46bb-ba04-67d06a415573'), UUID('083d9deb-aab6-48e9-9e73-80c4f63676d5'))
INFO      sqlalchemy.engine.Engine                  [cached since 318.9s ago] (0, UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'), UUID('fe09f04f-d026-46bb-ba04-67d06a415573'), UUID('083d9deb-aab6-48e9-9e73-80c4f63676d5'))
2026-04-06 02:19:19,766 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:19:19,790 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:19:19,791 INFO sqlalchemy.engine.Engine SELECT buckets.id, buckets.user_id, buckets.name, buckets.description, buckets.mcp_url, buckets.mcp_token, buckets.account_mcp_url, buckets.account_mcp_token, buckets.color, buckets.icon, buckets.is_public, buckets.storage_used, buckets.created_at, buckets.updated_at 
FROM buckets 
WHERE buckets.user_id = $1::UUID ORDER BY buckets.updated_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id, buckets.user_id, buckets.name, buckets.description, buckets.mcp_url, buckets.mcp_token, buckets.account_mcp_url, buckets.account_mcp_token, buckets.color, buckets.icon, buckets.is_public, buckets.storage_used, buckets.created_at, buckets.updated_at 
FROM buckets 
WHERE buckets.user_id = $1::UUID ORDER BY buckets.updated_at DESC
2026-04-06 02:19:19,792 INFO sqlalchemy.engine.Engine [cached since 319s ago] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'),)
INFO      sqlalchemy.engine.Engine                  [cached since 319s ago] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'),)
2026-04-06 02:19:19,797 INFO sqlalchemy.engine.Engine SELECT files.bucket_id, count(files.id) AS count_1, coalesce(sum(files.size), $1::INTEGER) AS coalesce_1 
FROM files 
WHERE files.bucket_id IN ($2::UUID, $3::UUID, $4::UUID) GROUP BY files.bucket_id
INFO      sqlalchemy.engine.Engine                  SELECT files.bucket_id, count(files.id) AS count_1, coalesce(sum(files.size), $1::INTEGER) AS coalesce_1 
FROM files 
WHERE files.bucket_id IN ($2::UUID, $3::UUID, $4::UUID) GROUP BY files.bucket_id
2026-04-06 02:19:19,797 INFO sqlalchemy.engine.Engine [cached since 318.9s ago] (0, UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'), UUID('fe09f04f-d026-46bb-ba04-67d06a415573'), UUID('083d9deb-aab6-48e9-9e73-80c4f63676d5'))
INFO      sqlalchemy.engine.Engine                  [cached since 318.9s ago] (0, UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'), UUID('fe09f04f-d026-46bb-ba04-67d06a415573'), UUID('083d9deb-aab6-48e9-9e73-80c4f63676d5'))
2026-04-06 02:19:19,800 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:19:19,951 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:19:19,952 INFO sqlalchemy.engine.Engine SELECT buckets.id, buckets.user_id, buckets.name, buckets.description, buckets.mcp_url, buckets.mcp_token, buckets.account_mcp_url, buckets.account_mcp_token, buckets.color, buckets.icon, buckets.is_public, buckets.storage_used, buckets.created_at, buckets.updated_at 
FROM buckets 
WHERE buckets.user_id = $1::UUID ORDER BY buckets.updated_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id, buckets.user_id, buckets.name, buckets.description, buckets.mcp_url, buckets.mcp_token, buckets.account_mcp_url, buckets.account_mcp_token, buckets.color, buckets.icon, buckets.is_public, buckets.storage_used, buckets.created_at, buckets.updated_at 
FROM buckets 
WHERE buckets.user_id = $1::UUID ORDER BY buckets.updated_at DESC
2026-04-06 02:19:19,953 INFO sqlalchemy.engine.Engine [cached since 319.1s ago] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'),)
INFO      sqlalchemy.engine.Engine                  [cached since 319.1s ago] (UUID('0dd290dd-8a7d-4be6-a48a-a9dd49c30013'),)
2026-04-06 02:19:19,959 INFO sqlalchemy.engine.Engine SELECT files.bucket_id, count(files.id) AS count_1, coalesce(sum(files.size), $1::INTEGER) AS coalesce_1 
FROM files 
WHERE files.bucket_id IN ($2::UUID, $3::UUID, $4::UUID) GROUP BY files.bucket_id
INFO      sqlalchemy.engine.Engine                  SELECT files.bucket_id, count(files.id) AS count_1, coalesce(sum(files.size), $1::INTEGER) AS coalesce_1 
FROM files 
WHERE files.bucket_id IN ($2::UUID, $3::UUID, $4::UUID) GROUP BY files.bucket_id
2026-04-06 02:19:19,960 INFO sqlalchemy.engine.Engine [cached since 319.1s ago] (0, UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'), UUID('fe09f04f-d026-46bb-ba04-67d06a415573'), UUID('083d9deb-aab6-48e9-9e73-80c4f63676d5'))
INFO      sqlalchemy.engine.Engine                  [cached since 319.1s ago] (0, UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'), UUID('fe09f04f-d026-46bb-ba04-67d06a415573'), UUID('083d9deb-aab6-48e9-9e73-80c4f63676d5'))
2026-04-06 02:19:19,962 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:19:19,963 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:19:19,964 INFO sqlalchemy.engine.Engine [cached since 308.8s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 308.8s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:19:19,967 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:19:19,971 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
2026-04-06 02:19:19,972 INFO sqlalchemy.engine.Engine [cached since 308.7s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 308.7s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:19:19,974 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:19:20,025 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:19:20,027 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:19:20,027 INFO sqlalchemy.engine.Engine [cached since 308.8s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 308.8s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:19:20,029 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:19:20,030 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:19:20,030 INFO sqlalchemy.engine.Engine [cached since 308.8s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 308.8s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:19:20,033 INFO sqlalchemy.engine.Engine SELECT files.id AS files_id, files.bucket_id AS files_bucket_id, files.user_id AS files_user_id, files.category_id AS files_category_id, files.name AS files_name, files.type AS files_type, files.size AS files_size, files.r2_path AS files_r2_path, files.layout_json_path AS files_layout_json_path, files.status AS files_status, files.page_count AS files_page_count, files.version AS files_version, files.is_agent_written AS files_is_agent_written, files.created_at AS files_created_at, files.updated_at AS files_updated_at 
FROM files 
WHERE files.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT files.id AS files_id, files.bucket_id AS files_bucket_id, files.user_id AS files_user_id, files.category_id AS files_category_id, files.name AS files_name, files.type AS files_type, files.size AS files_size, files.r2_path AS files_r2_path, files.layout_json_path AS files_layout_json_path, files.status AS files_status, files.page_count AS files_page_count, files.version AS files_version, files.is_agent_written AS files_is_agent_written, files.created_at AS files_created_at, files.updated_at AS files_updated_at 
FROM files 
WHERE files.id = $1::UUID
2026-04-06 02:19:20,034 INFO sqlalchemy.engine.Engine [cached since 294.2s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
INFO      sqlalchemy.engine.Engine                  [cached since 294.2s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
2026-04-06 02:19:20,038 INFO sqlalchemy.engine.Engine SELECT files.id AS files_id, files.bucket_id AS files_bucket_id, files.user_id AS files_user_id, files.category_id AS files_category_id, files.name AS files_name, files.type AS files_type, files.size AS files_size, files.r2_path AS files_r2_path, files.layout_json_path AS files_layout_json_path, files.status AS files_status, files.page_count AS files_page_count, files.version AS files_version, files.is_agent_written AS files_is_agent_written, files.created_at AS files_created_at, files.updated_at AS files_updated_at 
FROM files 
WHERE files.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT files.id AS files_id, files.bucket_id AS files_bucket_id, files.user_id AS files_user_id, files.category_id AS files_category_id, files.name AS files_name, files.type AS files_type, files.size AS files_size, files.r2_path AS files_r2_path, files.layout_json_path AS files_layout_json_path, files.status AS files_status, files.page_count AS files_page_count, files.version AS files_version, files.is_agent_written AS files_is_agent_written, files.created_at AS files_created_at, files.updated_at AS files_updated_at 
FROM files 
WHERE files.id = $1::UUID
2026-04-06 02:19:20,038 INFO sqlalchemy.engine.Engine [cached since 294.2s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
INFO      sqlalchemy.engine.Engine                  [cached since 294.2s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
2026-04-06 02:19:20,042 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:19:20,049 INFO sqlalchemy.engine.Engine SELECT investigation_events.id, investigation_events.file_id, investigation_events.event, investigation_events.status, investigation_events.metadata, investigation_events.created_at 
FROM investigation_events 
WHERE investigation_events.file_id = $1::UUID ORDER BY investigation_events.created_at ASC, investigation_events.event ASC
INFO      sqlalchemy.engine.Engine                  SELECT investigation_events.id, investigation_events.file_id, investigation_events.event, investigation_events.status, investigation_events.metadata, investigation_events.created_at 
FROM investigation_events 
WHERE investigation_events.file_id = $1::UUID ORDER BY investigation_events.created_at ASC, investigation_events.event ASC
2026-04-06 02:19:20,050 INFO sqlalchemy.engine.Engine [generated in 0.00135s] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
INFO      sqlalchemy.engine.Engine                  [generated in 0.00135s] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
2026-04-06 02:19:20,191 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:19:20,223 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:19:20,224 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:19:20,225 INFO sqlalchemy.engine.Engine [cached since 309s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 309s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:19:20,228 INFO sqlalchemy.engine.Engine SELECT files.id AS files_id, files.bucket_id AS files_bucket_id, files.user_id AS files_user_id, files.category_id AS files_category_id, files.name AS files_name, files.type AS files_type, files.size AS files_size, files.r2_path AS files_r2_path, files.layout_json_path AS files_layout_json_path, files.status AS files_status, files.page_count AS files_page_count, files.version AS files_version, files.is_agent_written AS files_is_agent_written, files.created_at AS files_created_at, files.updated_at AS files_updated_at 
FROM files 
WHERE files.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT files.id AS files_id, files.bucket_id AS files_bucket_id, files.user_id AS files_user_id, files.category_id AS files_category_id, files.name AS files_name, files.type AS files_type, files.size AS files_size, files.r2_path AS files_r2_path, files.layout_json_path AS files_layout_json_path, files.status AS files_status, files.page_count AS files_page_count, files.version AS files_version, files.is_agent_written AS files_is_agent_written, files.created_at AS files_created_at, files.updated_at AS files_updated_at 
FROM files 
WHERE files.id = $1::UUID
2026-04-06 02:19:20,229 INFO sqlalchemy.engine.Engine [cached since 294.4s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
INFO      sqlalchemy.engine.Engine                  [cached since 294.4s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
2026-04-06 02:19:20,232 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:19:20,235 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:19:20,236 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:19:20,236 INFO sqlalchemy.engine.Engine [cached since 309s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 309s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:19:20,240 INFO sqlalchemy.engine.Engine SELECT files.id AS files_id, files.bucket_id AS files_bucket_id, files.user_id AS files_user_id, files.category_id AS files_category_id, files.name AS files_name, files.type AS files_type, files.size AS files_size, files.r2_path AS files_r2_path, files.layout_json_path AS files_layout_json_path, files.status AS files_status, files.page_count AS files_page_count, files.version AS files_version, files.is_agent_written AS files_is_agent_written, files.created_at AS files_created_at, files.updated_at AS files_updated_at 
FROM files 
WHERE files.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT files.id AS files_id, files.bucket_id AS files_bucket_id, files.user_id AS files_user_id, files.category_id AS files_category_id, files.name AS files_name, files.type AS files_type, files.size AS files_size, files.r2_path AS files_r2_path, files.layout_json_path AS files_layout_json_path, files.status AS files_status, files.page_count AS files_page_count, files.version AS files_version, files.is_agent_written AS files_is_agent_written, files.created_at AS files_created_at, files.updated_at AS files_updated_at 
FROM files 
WHERE files.id = $1::UUID
2026-04-06 02:19:20,241 INFO sqlalchemy.engine.Engine [cached since 294.4s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
INFO      sqlalchemy.engine.Engine                  [cached since 294.4s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
2026-04-06 02:19:20,245 INFO sqlalchemy.engine.Engine SELECT investigation_events.id, investigation_events.file_id, investigation_events.event, investigation_events.status, investigation_events.metadata, investigation_events.created_at 
FROM investigation_events 
WHERE investigation_events.file_id = $1::UUID ORDER BY investigation_events.created_at ASC, investigation_events.event ASC
INFO      sqlalchemy.engine.Engine                  SELECT investigation_events.id, investigation_events.file_id, investigation_events.event, investigation_events.status, investigation_events.metadata, investigation_events.created_at 
FROM investigation_events 
WHERE investigation_events.file_id = $1::UUID ORDER BY investigation_events.created_at ASC, investigation_events.event ASC
2026-04-06 02:19:20,246 INFO sqlalchemy.engine.Engine [cached since 0.1972s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
INFO      sqlalchemy.engine.Engine                  [cached since 0.1972s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
2026-04-06 02:19:20,251 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:19:21,269 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:19:21,270 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:19:21,271 INFO sqlalchemy.engine.Engine [cached since 310.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 310.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:19:21,274 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
2026-04-06 02:19:21,275 INFO sqlalchemy.engine.Engine [cached since 310s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 310s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:19:21,277 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:19:22,788 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:19:22,790 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:19:22,791 INFO sqlalchemy.engine.Engine [cached since 311.6s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 311.6s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:19:22,793 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:19:22,794 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:19:22,794 INFO sqlalchemy.engine.Engine [cached since 311.6s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 311.6s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:19:22,797 INFO sqlalchemy.engine.Engine SELECT files.id AS files_id, files.bucket_id AS files_bucket_id, files.user_id AS files_user_id, files.category_id AS files_category_id, files.name AS files_name, files.type AS files_type, files.size AS files_size, files.r2_path AS files_r2_path, files.layout_json_path AS files_layout_json_path, files.status AS files_status, files.page_count AS files_page_count, files.version AS files_version, files.is_agent_written AS files_is_agent_written, files.created_at AS files_created_at, files.updated_at AS files_updated_at 
FROM files 
WHERE files.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT files.id AS files_id, files.bucket_id AS files_bucket_id, files.user_id AS files_user_id, files.category_id AS files_category_id, files.name AS files_name, files.type AS files_type, files.size AS files_size, files.r2_path AS files_r2_path, files.layout_json_path AS files_layout_json_path, files.status AS files_status, files.page_count AS files_page_count, files.version AS files_version, files.is_agent_written AS files_is_agent_written, files.created_at AS files_created_at, files.updated_at AS files_updated_at 
FROM files 
WHERE files.id = $1::UUID
2026-04-06 02:19:22,798 INFO sqlalchemy.engine.Engine [cached since 297s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
INFO      sqlalchemy.engine.Engine                  [cached since 297s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
2026-04-06 02:19:22,801 INFO sqlalchemy.engine.Engine SELECT investigation_events.id, investigation_events.file_id, investigation_events.event, investigation_events.status, investigation_events.metadata, investigation_events.created_at 
FROM investigation_events 
WHERE investigation_events.file_id = $1::UUID ORDER BY investigation_events.created_at ASC, investigation_events.event ASC
INFO      sqlalchemy.engine.Engine                  SELECT investigation_events.id, investigation_events.file_id, investigation_events.event, investigation_events.status, investigation_events.metadata, investigation_events.created_at 
FROM investigation_events 
WHERE investigation_events.file_id = $1::UUID ORDER BY investigation_events.created_at ASC, investigation_events.event ASC
2026-04-06 02:19:22,802 INFO sqlalchemy.engine.Engine [cached since 2.754s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
INFO      sqlalchemy.engine.Engine                  [cached since 2.754s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
2026-04-06 02:19:22,806 INFO sqlalchemy.engine.Engine SELECT files.id AS files_id, files.bucket_id AS files_bucket_id, files.user_id AS files_user_id, files.category_id AS files_category_id, files.name AS files_name, files.type AS files_type, files.size AS files_size, files.r2_path AS files_r2_path, files.layout_json_path AS files_layout_json_path, files.status AS files_status, files.page_count AS files_page_count, files.version AS files_version, files.is_agent_written AS files_is_agent_written, files.created_at AS files_created_at, files.updated_at AS files_updated_at 
FROM files 
WHERE files.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT files.id AS files_id, files.bucket_id AS files_bucket_id, files.user_id AS files_user_id, files.category_id AS files_category_id, files.name AS files_name, files.type AS files_type, files.size AS files_size, files.r2_path AS files_r2_path, files.layout_json_path AS files_layout_json_path, files.status AS files_status, files.page_count AS files_page_count, files.version AS files_version, files.is_agent_written AS files_is_agent_written, files.created_at AS files_created_at, files.updated_at AS files_updated_at 
FROM files 
WHERE files.id = $1::UUID
2026-04-06 02:19:22,808 INFO sqlalchemy.engine.Engine [cached since 297s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
INFO      sqlalchemy.engine.Engine                  [cached since 297s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
2026-04-06 02:19:22,814 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:19:22,950 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
Inference Embeddings:   0%|▎                                                                    | 1/205 [02:14<7:38:16, 134.79s/it]2026-04-06 02:19:25,484 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:19:25,485 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:19:25,485 INFO sqlalchemy.engine.Engine [cached since 314.3s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 314.3s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:19:25,486 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:19:25,486 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:19:25,487 INFO sqlalchemy.engine.Engine [cached since 314.3s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 314.3s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:19:25,489 INFO sqlalchemy.engine.Engine SELECT files.id AS files_id, files.bucket_id AS files_bucket_id, files.user_id AS files_user_id, files.category_id AS files_category_id, files.name AS files_name, files.type AS files_type, files.size AS files_size, files.r2_path AS files_r2_path, files.layout_json_path AS files_layout_json_path, files.status AS files_status, files.page_count AS files_page_count, files.version AS files_version, files.is_agent_written AS files_is_agent_written, files.created_at AS files_created_at, files.updated_at AS files_updated_at 
FROM files 
WHERE files.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT files.id AS files_id, files.bucket_id AS files_bucket_id, files.user_id AS files_user_id, files.category_id AS files_category_id, files.name AS files_name, files.type AS files_type, files.size AS files_size, files.r2_path AS files_r2_path, files.layout_json_path AS files_layout_json_path, files.status AS files_status, files.page_count AS files_page_count, files.version AS files_version, files.is_agent_written AS files_is_agent_written, files.created_at AS files_created_at, files.updated_at AS files_updated_at 
FROM files 
WHERE files.id = $1::UUID
2026-04-06 02:19:25,490 INFO sqlalchemy.engine.Engine [cached since 299.7s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
INFO      sqlalchemy.engine.Engine                  [cached since 299.7s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
2026-04-06 02:19:25,491 INFO sqlalchemy.engine.Engine SELECT files.id AS files_id, files.bucket_id AS files_bucket_id, files.user_id AS files_user_id, files.category_id AS files_category_id, files.name AS files_name, files.type AS files_type, files.size AS files_size, files.r2_path AS files_r2_path, files.layout_json_path AS files_layout_json_path, files.status AS files_status, files.page_count AS files_page_count, files.version AS files_version, files.is_agent_written AS files_is_agent_written, files.created_at AS files_created_at, files.updated_at AS files_updated_at 
FROM files 
WHERE files.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT files.id AS files_id, files.bucket_id AS files_bucket_id, files.user_id AS files_user_id, files.category_id AS files_category_id, files.name AS files_name, files.type AS files_type, files.size AS files_size, files.r2_path AS files_r2_path, files.layout_json_path AS files_layout_json_path, files.status AS files_status, files.page_count AS files_page_count, files.version AS files_version, files.is_agent_written AS files_is_agent_written, files.created_at AS files_created_at, files.updated_at AS files_updated_at 
FROM files 
WHERE files.id = $1::UUID
2026-04-06 02:19:25,492 INFO sqlalchemy.engine.Engine [cached since 299.7s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
INFO      sqlalchemy.engine.Engine                  [cached since 299.7s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
2026-04-06 02:19:25,494 INFO sqlalchemy.engine.Engine SELECT investigation_events.id, investigation_events.file_id, investigation_events.event, investigation_events.status, investigation_events.metadata, investigation_events.created_at 
FROM investigation_events 
WHERE investigation_events.file_id = $1::UUID ORDER BY investigation_events.created_at ASC, investigation_events.event ASC
INFO      sqlalchemy.engine.Engine                  SELECT investigation_events.id, investigation_events.file_id, investigation_events.event, investigation_events.status, investigation_events.metadata, investigation_events.created_at 
FROM investigation_events 
WHERE investigation_events.file_id = $1::UUID ORDER BY investigation_events.created_at ASC, investigation_events.event ASC
2026-04-06 02:19:25,494 INFO sqlalchemy.engine.Engine [cached since 5.446s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
INFO      sqlalchemy.engine.Engine                  [cached since 5.446s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
2026-04-06 02:19:25,496 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:19:25,499 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:19:26,271 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:19:26,272 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:19:26,272 INFO sqlalchemy.engine.Engine [cached since 315.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 315.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:19:26,275 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
2026-04-06 02:19:26,276 INFO sqlalchemy.engine.Engine [cached since 315s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 315s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:19:26,278 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:19:28,053 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:19:28,055 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:19:28,056 INFO sqlalchemy.engine.Engine [cached since 316.9s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 316.9s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:19:28,060 INFO sqlalchemy.engine.Engine SELECT files.id AS files_id, files.bucket_id AS files_bucket_id, files.user_id AS files_user_id, files.category_id AS files_category_id, files.name AS files_name, files.type AS files_type, files.size AS files_size, files.r2_path AS files_r2_path, files.layout_json_path AS files_layout_json_path, files.status AS files_status, files.page_count AS files_page_count, files.version AS files_version, files.is_agent_written AS files_is_agent_written, files.created_at AS files_created_at, files.updated_at AS files_updated_at 
FROM files 
WHERE files.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT files.id AS files_id, files.bucket_id AS files_bucket_id, files.user_id AS files_user_id, files.category_id AS files_category_id, files.name AS files_name, files.type AS files_type, files.size AS files_size, files.r2_path AS files_r2_path, files.layout_json_path AS files_layout_json_path, files.status AS files_status, files.page_count AS files_page_count, files.version AS files_version, files.is_agent_written AS files_is_agent_written, files.created_at AS files_created_at, files.updated_at AS files_updated_at 
FROM files 
WHERE files.id = $1::UUID
2026-04-06 02:19:28,061 INFO sqlalchemy.engine.Engine [cached since 302.3s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
INFO      sqlalchemy.engine.Engine                  [cached since 302.3s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
2026-04-06 02:19:28,064 INFO sqlalchemy.engine.Engine SELECT investigation_events.id, investigation_events.file_id, investigation_events.event, investigation_events.status, investigation_events.metadata, investigation_events.created_at 
FROM investigation_events 
WHERE investigation_events.file_id = $1::UUID ORDER BY investigation_events.created_at ASC, investigation_events.event ASC
INFO      sqlalchemy.engine.Engine                  SELECT investigation_events.id, investigation_events.file_id, investigation_events.event, investigation_events.status, investigation_events.metadata, investigation_events.created_at 
FROM investigation_events 
WHERE investigation_events.file_id = $1::UUID ORDER BY investigation_events.created_at ASC, investigation_events.event ASC
2026-04-06 02:19:28,065 INFO sqlalchemy.engine.Engine [cached since 8.016s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
INFO      sqlalchemy.engine.Engine                  [cached since 8.016s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
2026-04-06 02:19:28,066 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:19:28,067 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:19:28,068 INFO sqlalchemy.engine.Engine [cached since 316.9s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 316.9s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:19:28,074 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:19:28,077 INFO sqlalchemy.engine.Engine SELECT files.id AS files_id, files.bucket_id AS files_bucket_id, files.user_id AS files_user_id, files.category_id AS files_category_id, files.name AS files_name, files.type AS files_type, files.size AS files_size, files.r2_path AS files_r2_path, files.layout_json_path AS files_layout_json_path, files.status AS files_status, files.page_count AS files_page_count, files.version AS files_version, files.is_agent_written AS files_is_agent_written, files.created_at AS files_created_at, files.updated_at AS files_updated_at 
FROM files 
WHERE files.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT files.id AS files_id, files.bucket_id AS files_bucket_id, files.user_id AS files_user_id, files.category_id AS files_category_id, files.name AS files_name, files.type AS files_type, files.size AS files_size, files.r2_path AS files_r2_path, files.layout_json_path AS files_layout_json_path, files.status AS files_status, files.page_count AS files_page_count, files.version AS files_version, files.is_agent_written AS files_is_agent_written, files.created_at AS files_created_at, files.updated_at AS files_updated_at 
FROM files 
WHERE files.id = $1::UUID
2026-04-06 02:19:28,078 INFO sqlalchemy.engine.Engine [cached since 302.3s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
INFO      sqlalchemy.engine.Engine                  [cached since 302.3s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
2026-04-06 02:19:28,081 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:19:30,707 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:19:30,708 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:19:30,709 INFO sqlalchemy.engine.Engine [cached since 319.5s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 319.5s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:19:30,709 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:19:30,710 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:19:30,710 INFO sqlalchemy.engine.Engine [cached since 319.5s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 319.5s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:19:30,714 INFO sqlalchemy.engine.Engine SELECT files.id AS files_id, files.bucket_id AS files_bucket_id, files.user_id AS files_user_id, files.category_id AS files_category_id, files.name AS files_name, files.type AS files_type, files.size AS files_size, files.r2_path AS files_r2_path, files.layout_json_path AS files_layout_json_path, files.status AS files_status, files.page_count AS files_page_count, files.version AS files_version, files.is_agent_written AS files_is_agent_written, files.created_at AS files_created_at, files.updated_at AS files_updated_at 
FROM files 
WHERE files.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT files.id AS files_id, files.bucket_id AS files_bucket_id, files.user_id AS files_user_id, files.category_id AS files_category_id, files.name AS files_name, files.type AS files_type, files.size AS files_size, files.r2_path AS files_r2_path, files.layout_json_path AS files_layout_json_path, files.status AS files_status, files.page_count AS files_page_count, files.version AS files_version, files.is_agent_written AS files_is_agent_written, files.created_at AS files_created_at, files.updated_at AS files_updated_at 
FROM files 
WHERE files.id = $1::UUID
2026-04-06 02:19:30,714 INFO sqlalchemy.engine.Engine [cached since 304.9s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
INFO      sqlalchemy.engine.Engine                  [cached since 304.9s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
2026-04-06 02:19:30,718 INFO sqlalchemy.engine.Engine SELECT investigation_events.id, investigation_events.file_id, investigation_events.event, investigation_events.status, investigation_events.metadata, investigation_events.created_at 
FROM investigation_events 
WHERE investigation_events.file_id = $1::UUID ORDER BY investigation_events.created_at ASC, investigation_events.event ASC
INFO      sqlalchemy.engine.Engine                  SELECT investigation_events.id, investigation_events.file_id, investigation_events.event, investigation_events.status, investigation_events.metadata, investigation_events.created_at 
FROM investigation_events 
WHERE investigation_events.file_id = $1::UUID ORDER BY investigation_events.created_at ASC, investigation_events.event ASC
2026-04-06 02:19:30,718 INFO sqlalchemy.engine.Engine [cached since 10.67s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
INFO      sqlalchemy.engine.Engine                  [cached since 10.67s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
2026-04-06 02:19:30,722 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:19:30,724 INFO sqlalchemy.engine.Engine SELECT files.id AS files_id, files.bucket_id AS files_bucket_id, files.user_id AS files_user_id, files.category_id AS files_category_id, files.name AS files_name, files.type AS files_type, files.size AS files_size, files.r2_path AS files_r2_path, files.layout_json_path AS files_layout_json_path, files.status AS files_status, files.page_count AS files_page_count, files.version AS files_version, files.is_agent_written AS files_is_agent_written, files.created_at AS files_created_at, files.updated_at AS files_updated_at 
FROM files 
WHERE files.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT files.id AS files_id, files.bucket_id AS files_bucket_id, files.user_id AS files_user_id, files.category_id AS files_category_id, files.name AS files_name, files.type AS files_type, files.size AS files_size, files.r2_path AS files_r2_path, files.layout_json_path AS files_layout_json_path, files.status AS files_status, files.page_count AS files_page_count, files.version AS files_version, files.is_agent_written AS files_is_agent_written, files.created_at AS files_created_at, files.updated_at AS files_updated_at 
FROM files 
WHERE files.id = $1::UUID
2026-04-06 02:19:30,724 INFO sqlalchemy.engine.Engine [cached since 304.9s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
INFO      sqlalchemy.engine.Engine                  [cached since 304.9s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
2026-04-06 02:19:30,727 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:19:31,270 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:19:31,271 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:19:31,271 INFO sqlalchemy.engine.Engine [cached since 320.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 320.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:19:31,274 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
2026-04-06 02:19:31,275 INFO sqlalchemy.engine.Engine [cached since 320s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 320s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:19:31,277 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:19:33,263 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:19:33,265 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:19:33,266 INFO sqlalchemy.engine.Engine [cached since 322.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 322.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:19:33,267 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:19:33,269 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:19:33,269 INFO sqlalchemy.engine.Engine [cached since 322.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 322.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:19:33,273 INFO sqlalchemy.engine.Engine SELECT files.id AS files_id, files.bucket_id AS files_bucket_id, files.user_id AS files_user_id, files.category_id AS files_category_id, files.name AS files_name, files.type AS files_type, files.size AS files_size, files.r2_path AS files_r2_path, files.layout_json_path AS files_layout_json_path, files.status AS files_status, files.page_count AS files_page_count, files.version AS files_version, files.is_agent_written AS files_is_agent_written, files.created_at AS files_created_at, files.updated_at AS files_updated_at 
FROM files 
WHERE files.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT files.id AS files_id, files.bucket_id AS files_bucket_id, files.user_id AS files_user_id, files.category_id AS files_category_id, files.name AS files_name, files.type AS files_type, files.size AS files_size, files.r2_path AS files_r2_path, files.layout_json_path AS files_layout_json_path, files.status AS files_status, files.page_count AS files_page_count, files.version AS files_version, files.is_agent_written AS files_is_agent_written, files.created_at AS files_created_at, files.updated_at AS files_updated_at 
FROM files 
WHERE files.id = $1::UUID
2026-04-06 02:19:33,274 INFO sqlalchemy.engine.Engine [cached since 307.5s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
INFO      sqlalchemy.engine.Engine                  [cached since 307.5s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
2026-04-06 02:19:33,278 INFO sqlalchemy.engine.Engine SELECT investigation_events.id, investigation_events.file_id, investigation_events.event, investigation_events.status, investigation_events.metadata, investigation_events.created_at 
FROM investigation_events 
WHERE investigation_events.file_id = $1::UUID ORDER BY investigation_events.created_at ASC, investigation_events.event ASC
INFO      sqlalchemy.engine.Engine                  SELECT investigation_events.id, investigation_events.file_id, investigation_events.event, investigation_events.status, investigation_events.metadata, investigation_events.created_at 
FROM investigation_events 
WHERE investigation_events.file_id = $1::UUID ORDER BY investigation_events.created_at ASC, investigation_events.event ASC
2026-04-06 02:19:33,278 INFO sqlalchemy.engine.Engine [cached since 13.23s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
INFO      sqlalchemy.engine.Engine                  [cached since 13.23s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
2026-04-06 02:19:33,284 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:19:33,286 INFO sqlalchemy.engine.Engine SELECT files.id AS files_id, files.bucket_id AS files_bucket_id, files.user_id AS files_user_id, files.category_id AS files_category_id, files.name AS files_name, files.type AS files_type, files.size AS files_size, files.r2_path AS files_r2_path, files.layout_json_path AS files_layout_json_path, files.status AS files_status, files.page_count AS files_page_count, files.version AS files_version, files.is_agent_written AS files_is_agent_written, files.created_at AS files_created_at, files.updated_at AS files_updated_at 
FROM files 
WHERE files.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT files.id AS files_id, files.bucket_id AS files_bucket_id, files.user_id AS files_user_id, files.category_id AS files_category_id, files.name AS files_name, files.type AS files_type, files.size AS files_size, files.r2_path AS files_r2_path, files.layout_json_path AS files_layout_json_path, files.status AS files_status, files.page_count AS files_page_count, files.version AS files_version, files.is_agent_written AS files_is_agent_written, files.created_at AS files_created_at, files.updated_at AS files_updated_at 
FROM files 
WHERE files.id = $1::UUID
2026-04-06 02:19:33,287 INFO sqlalchemy.engine.Engine [cached since 307.5s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
INFO      sqlalchemy.engine.Engine                  [cached since 307.5s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
2026-04-06 02:19:33,291 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:19:35,306 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:19:35,307 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:19:35,307 INFO sqlalchemy.engine.Engine [cached since 324.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 324.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:19:35,310 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
2026-04-06 02:19:35,311 INFO sqlalchemy.engine.Engine [cached since 324.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 324.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:19:35,313 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:19:36,277 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:19:36,279 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:19:36,279 INFO sqlalchemy.engine.Engine [cached since 325.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 325.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:19:36,283 INFO sqlalchemy.engine.Engine SELECT files.id AS files_id, files.bucket_id AS files_bucket_id, files.user_id AS files_user_id, files.category_id AS files_category_id, files.name AS files_name, files.type AS files_type, files.size AS files_size, files.r2_path AS files_r2_path, files.layout_json_path AS files_layout_json_path, files.status AS files_status, files.page_count AS files_page_count, files.version AS files_version, files.is_agent_written AS files_is_agent_written, files.created_at AS files_created_at, files.updated_at AS files_updated_at 
FROM files 
WHERE files.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT files.id AS files_id, files.bucket_id AS files_bucket_id, files.user_id AS files_user_id, files.category_id AS files_category_id, files.name AS files_name, files.type AS files_type, files.size AS files_size, files.r2_path AS files_r2_path, files.layout_json_path AS files_layout_json_path, files.status AS files_status, files.page_count AS files_page_count, files.version AS files_version, files.is_agent_written AS files_is_agent_written, files.created_at AS files_created_at, files.updated_at AS files_updated_at 
FROM files 
WHERE files.id = $1::UUID
2026-04-06 02:19:36,283 INFO sqlalchemy.engine.Engine [cached since 310.5s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
INFO      sqlalchemy.engine.Engine                  [cached since 310.5s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
2026-04-06 02:19:36,286 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:19:36,287 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:19:36,288 INFO sqlalchemy.engine.Engine [cached since 325.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 325.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:19:36,290 INFO sqlalchemy.engine.Engine SELECT investigation_events.id, investigation_events.file_id, investigation_events.event, investigation_events.status, investigation_events.metadata, investigation_events.created_at 
FROM investigation_events 
WHERE investigation_events.file_id = $1::UUID ORDER BY investigation_events.created_at ASC, investigation_events.event ASC
INFO      sqlalchemy.engine.Engine                  SELECT investigation_events.id, investigation_events.file_id, investigation_events.event, investigation_events.status, investigation_events.metadata, investigation_events.created_at 
FROM investigation_events 
WHERE investigation_events.file_id = $1::UUID ORDER BY investigation_events.created_at ASC, investigation_events.event ASC
2026-04-06 02:19:36,291 INFO sqlalchemy.engine.Engine [cached since 16.24s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
INFO      sqlalchemy.engine.Engine                  [cached since 16.24s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
2026-04-06 02:19:36,296 INFO sqlalchemy.engine.Engine SELECT files.id AS files_id, files.bucket_id AS files_bucket_id, files.user_id AS files_user_id, files.category_id AS files_category_id, files.name AS files_name, files.type AS files_type, files.size AS files_size, files.r2_path AS files_r2_path, files.layout_json_path AS files_layout_json_path, files.status AS files_status, files.page_count AS files_page_count, files.version AS files_version, files.is_agent_written AS files_is_agent_written, files.created_at AS files_created_at, files.updated_at AS files_updated_at 
FROM files 
WHERE files.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT files.id AS files_id, files.bucket_id AS files_bucket_id, files.user_id AS files_user_id, files.category_id AS files_category_id, files.name AS files_name, files.type AS files_type, files.size AS files_size, files.r2_path AS files_r2_path, files.layout_json_path AS files_layout_json_path, files.status AS files_status, files.page_count AS files_page_count, files.version AS files_version, files.is_agent_written AS files_is_agent_written, files.created_at AS files_created_at, files.updated_at AS files_updated_at 
FROM files 
WHERE files.id = $1::UUID
2026-04-06 02:19:36,298 INFO sqlalchemy.engine.Engine [cached since 310.5s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
INFO      sqlalchemy.engine.Engine                  [cached since 310.5s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
2026-04-06 02:19:36,302 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:19:36,305 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:19:39,299 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:19:39,301 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:19:39,302 INFO sqlalchemy.engine.Engine [cached since 328.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 328.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:19:39,304 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:19:39,305 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:19:39,306 INFO sqlalchemy.engine.Engine [cached since 328.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 328.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:19:39,309 INFO sqlalchemy.engine.Engine SELECT files.id AS files_id, files.bucket_id AS files_bucket_id, files.user_id AS files_user_id, files.category_id AS files_category_id, files.name AS files_name, files.type AS files_type, files.size AS files_size, files.r2_path AS files_r2_path, files.layout_json_path AS files_layout_json_path, files.status AS files_status, files.page_count AS files_page_count, files.version AS files_version, files.is_agent_written AS files_is_agent_written, files.created_at AS files_created_at, files.updated_at AS files_updated_at 
FROM files 
WHERE files.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT files.id AS files_id, files.bucket_id AS files_bucket_id, files.user_id AS files_user_id, files.category_id AS files_category_id, files.name AS files_name, files.type AS files_type, files.size AS files_size, files.r2_path AS files_r2_path, files.layout_json_path AS files_layout_json_path, files.status AS files_status, files.page_count AS files_page_count, files.version AS files_version, files.is_agent_written AS files_is_agent_written, files.created_at AS files_created_at, files.updated_at AS files_updated_at 
FROM files 
WHERE files.id = $1::UUID
2026-04-06 02:19:39,310 INFO sqlalchemy.engine.Engine [cached since 313.5s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
INFO      sqlalchemy.engine.Engine                  [cached since 313.5s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
2026-04-06 02:19:39,314 INFO sqlalchemy.engine.Engine SELECT investigation_events.id, investigation_events.file_id, investigation_events.event, investigation_events.status, investigation_events.metadata, investigation_events.created_at 
FROM investigation_events 
WHERE investigation_events.file_id = $1::UUID ORDER BY investigation_events.created_at ASC, investigation_events.event ASC
INFO      sqlalchemy.engine.Engine                  SELECT investigation_events.id, investigation_events.file_id, investigation_events.event, investigation_events.status, investigation_events.metadata, investigation_events.created_at 
FROM investigation_events 
WHERE investigation_events.file_id = $1::UUID ORDER BY investigation_events.created_at ASC, investigation_events.event ASC
2026-04-06 02:19:39,315 INFO sqlalchemy.engine.Engine [cached since 19.27s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
INFO      sqlalchemy.engine.Engine                  [cached since 19.27s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
2026-04-06 02:19:39,320 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:19:39,322 INFO sqlalchemy.engine.Engine SELECT files.id AS files_id, files.bucket_id AS files_bucket_id, files.user_id AS files_user_id, files.category_id AS files_category_id, files.name AS files_name, files.type AS files_type, files.size AS files_size, files.r2_path AS files_r2_path, files.layout_json_path AS files_layout_json_path, files.status AS files_status, files.page_count AS files_page_count, files.version AS files_version, files.is_agent_written AS files_is_agent_written, files.created_at AS files_created_at, files.updated_at AS files_updated_at 
FROM files 
WHERE files.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT files.id AS files_id, files.bucket_id AS files_bucket_id, files.user_id AS files_user_id, files.category_id AS files_category_id, files.name AS files_name, files.type AS files_type, files.size AS files_size, files.r2_path AS files_r2_path, files.layout_json_path AS files_layout_json_path, files.status AS files_status, files.page_count AS files_page_count, files.version AS files_version, files.is_agent_written AS files_is_agent_written, files.created_at AS files_created_at, files.updated_at AS files_updated_at 
FROM files 
WHERE files.id = $1::UUID
2026-04-06 02:19:39,449 INFO sqlalchemy.engine.Engine [cached since 313.5s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
INFO      sqlalchemy.engine.Engine                  [cached since 313.5s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
2026-04-06 02:19:39,453 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:19:39,474 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:19:39,475 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:19:39,476 INFO sqlalchemy.engine.Engine [cached since 328.3s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 328.3s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:19:39,479 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
2026-04-06 02:19:39,480 INFO sqlalchemy.engine.Engine [cached since 328.3s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 328.3s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:19:39,483 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:19:41,988 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:19:41,990 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:19:41,991 INFO sqlalchemy.engine.Engine [cached since 330.8s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 330.8s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:19:41,992 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:19:41,993 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:19:41,993 INFO sqlalchemy.engine.Engine [cached since 330.8s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 330.8s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:19:41,998 INFO sqlalchemy.engine.Engine SELECT files.id AS files_id, files.bucket_id AS files_bucket_id, files.user_id AS files_user_id, files.category_id AS files_category_id, files.name AS files_name, files.type AS files_type, files.size AS files_size, files.r2_path AS files_r2_path, files.layout_json_path AS files_layout_json_path, files.status AS files_status, files.page_count AS files_page_count, files.version AS files_version, files.is_agent_written AS files_is_agent_written, files.created_at AS files_created_at, files.updated_at AS files_updated_at 
FROM files 
WHERE files.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT files.id AS files_id, files.bucket_id AS files_bucket_id, files.user_id AS files_user_id, files.category_id AS files_category_id, files.name AS files_name, files.type AS files_type, files.size AS files_size, files.r2_path AS files_r2_path, files.layout_json_path AS files_layout_json_path, files.status AS files_status, files.page_count AS files_page_count, files.version AS files_version, files.is_agent_written AS files_is_agent_written, files.created_at AS files_created_at, files.updated_at AS files_updated_at 
FROM files 
WHERE files.id = $1::UUID
2026-04-06 02:19:41,999 INFO sqlalchemy.engine.Engine [cached since 316.2s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
INFO      sqlalchemy.engine.Engine                  [cached since 316.2s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
2026-04-06 02:19:42,001 INFO sqlalchemy.engine.Engine SELECT files.id AS files_id, files.bucket_id AS files_bucket_id, files.user_id AS files_user_id, files.category_id AS files_category_id, files.name AS files_name, files.type AS files_type, files.size AS files_size, files.r2_path AS files_r2_path, files.layout_json_path AS files_layout_json_path, files.status AS files_status, files.page_count AS files_page_count, files.version AS files_version, files.is_agent_written AS files_is_agent_written, files.created_at AS files_created_at, files.updated_at AS files_updated_at 
FROM files 
WHERE files.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT files.id AS files_id, files.bucket_id AS files_bucket_id, files.user_id AS files_user_id, files.category_id AS files_category_id, files.name AS files_name, files.type AS files_type, files.size AS files_size, files.r2_path AS files_r2_path, files.layout_json_path AS files_layout_json_path, files.status AS files_status, files.page_count AS files_page_count, files.version AS files_version, files.is_agent_written AS files_is_agent_written, files.created_at AS files_created_at, files.updated_at AS files_updated_at 
FROM files 
WHERE files.id = $1::UUID
2026-04-06 02:19:42,002 INFO sqlalchemy.engine.Engine [cached since 316.2s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
INFO      sqlalchemy.engine.Engine                  [cached since 316.2s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
2026-04-06 02:19:42,006 INFO sqlalchemy.engine.Engine SELECT investigation_events.id, investigation_events.file_id, investigation_events.event, investigation_events.status, investigation_events.metadata, investigation_events.created_at 
FROM investigation_events 
WHERE investigation_events.file_id = $1::UUID ORDER BY investigation_events.created_at ASC, investigation_events.event ASC
INFO      sqlalchemy.engine.Engine                  SELECT investigation_events.id, investigation_events.file_id, investigation_events.event, investigation_events.status, investigation_events.metadata, investigation_events.created_at 
FROM investigation_events 
WHERE investigation_events.file_id = $1::UUID ORDER BY investigation_events.created_at ASC, investigation_events.event ASC
2026-04-06 02:19:42,007 INFO sqlalchemy.engine.Engine [cached since 21.96s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
INFO      sqlalchemy.engine.Engine                  [cached since 21.96s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
2026-04-06 02:19:42,010 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:19:42,018 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:19:44,272 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:19:44,274 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:19:44,275 INFO sqlalchemy.engine.Engine [cached since 333.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 333.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:19:44,279 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
2026-04-06 02:19:44,280 INFO sqlalchemy.engine.Engine [cached since 333.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 333.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:19:44,283 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:19:44,554 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:19:44,554 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:19:44,555 INFO sqlalchemy.engine.Engine [cached since 333.4s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 333.4s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:19:44,557 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:19:44,557 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:19:44,558 INFO sqlalchemy.engine.Engine [cached since 333.4s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 333.4s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:19:44,561 INFO sqlalchemy.engine.Engine SELECT files.id AS files_id, files.bucket_id AS files_bucket_id, files.user_id AS files_user_id, files.category_id AS files_category_id, files.name AS files_name, files.type AS files_type, files.size AS files_size, files.r2_path AS files_r2_path, files.layout_json_path AS files_layout_json_path, files.status AS files_status, files.page_count AS files_page_count, files.version AS files_version, files.is_agent_written AS files_is_agent_written, files.created_at AS files_created_at, files.updated_at AS files_updated_at 
FROM files 
WHERE files.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT files.id AS files_id, files.bucket_id AS files_bucket_id, files.user_id AS files_user_id, files.category_id AS files_category_id, files.name AS files_name, files.type AS files_type, files.size AS files_size, files.r2_path AS files_r2_path, files.layout_json_path AS files_layout_json_path, files.status AS files_status, files.page_count AS files_page_count, files.version AS files_version, files.is_agent_written AS files_is_agent_written, files.created_at AS files_created_at, files.updated_at AS files_updated_at 
FROM files 
WHERE files.id = $1::UUID
2026-04-06 02:19:44,561 INFO sqlalchemy.engine.Engine [cached since 318.8s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
INFO      sqlalchemy.engine.Engine                  [cached since 318.8s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
2026-04-06 02:19:44,565 INFO sqlalchemy.engine.Engine SELECT investigation_events.id, investigation_events.file_id, investigation_events.event, investigation_events.status, investigation_events.metadata, investigation_events.created_at 
FROM investigation_events 
WHERE investigation_events.file_id = $1::UUID ORDER BY investigation_events.created_at ASC, investigation_events.event ASC
INFO      sqlalchemy.engine.Engine                  SELECT investigation_events.id, investigation_events.file_id, investigation_events.event, investigation_events.status, investigation_events.metadata, investigation_events.created_at 
FROM investigation_events 
WHERE investigation_events.file_id = $1::UUID ORDER BY investigation_events.created_at ASC, investigation_events.event ASC
2026-04-06 02:19:44,566 INFO sqlalchemy.engine.Engine [cached since 24.52s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
INFO      sqlalchemy.engine.Engine                  [cached since 24.52s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
2026-04-06 02:19:44,568 INFO sqlalchemy.engine.Engine SELECT files.id AS files_id, files.bucket_id AS files_bucket_id, files.user_id AS files_user_id, files.category_id AS files_category_id, files.name AS files_name, files.type AS files_type, files.size AS files_size, files.r2_path AS files_r2_path, files.layout_json_path AS files_layout_json_path, files.status AS files_status, files.page_count AS files_page_count, files.version AS files_version, files.is_agent_written AS files_is_agent_written, files.created_at AS files_created_at, files.updated_at AS files_updated_at 
FROM files 
WHERE files.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT files.id AS files_id, files.bucket_id AS files_bucket_id, files.user_id AS files_user_id, files.category_id AS files_category_id, files.name AS files_name, files.type AS files_type, files.size AS files_size, files.r2_path AS files_r2_path, files.layout_json_path AS files_layout_json_path, files.status AS files_status, files.page_count AS files_page_count, files.version AS files_version, files.is_agent_written AS files_is_agent_written, files.created_at AS files_created_at, files.updated_at AS files_updated_at 
FROM files 
WHERE files.id = $1::UUID
2026-04-06 02:19:44,569 INFO sqlalchemy.engine.Engine [cached since 318.8s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
INFO      sqlalchemy.engine.Engine                  [cached since 318.8s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
2026-04-06 02:19:44,573 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:19:44,702 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:19:47,233 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:19:47,235 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:19:47,236 INFO sqlalchemy.engine.Engine [cached since 336s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 336s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:19:47,237 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:19:47,239 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:19:47,240 INFO sqlalchemy.engine.Engine [cached since 336s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 336s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:19:47,244 INFO sqlalchemy.engine.Engine SELECT files.id AS files_id, files.bucket_id AS files_bucket_id, files.user_id AS files_user_id, files.category_id AS files_category_id, files.name AS files_name, files.type AS files_type, files.size AS files_size, files.r2_path AS files_r2_path, files.layout_json_path AS files_layout_json_path, files.status AS files_status, files.page_count AS files_page_count, files.version AS files_version, files.is_agent_written AS files_is_agent_written, files.created_at AS files_created_at, files.updated_at AS files_updated_at 
FROM files 
WHERE files.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT files.id AS files_id, files.bucket_id AS files_bucket_id, files.user_id AS files_user_id, files.category_id AS files_category_id, files.name AS files_name, files.type AS files_type, files.size AS files_size, files.r2_path AS files_r2_path, files.layout_json_path AS files_layout_json_path, files.status AS files_status, files.page_count AS files_page_count, files.version AS files_version, files.is_agent_written AS files_is_agent_written, files.created_at AS files_created_at, files.updated_at AS files_updated_at 
FROM files 
WHERE files.id = $1::UUID
2026-04-06 02:19:47,245 INFO sqlalchemy.engine.Engine [cached since 321.4s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
INFO      sqlalchemy.engine.Engine                  [cached since 321.4s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
2026-04-06 02:19:47,248 INFO sqlalchemy.engine.Engine SELECT files.id AS files_id, files.bucket_id AS files_bucket_id, files.user_id AS files_user_id, files.category_id AS files_category_id, files.name AS files_name, files.type AS files_type, files.size AS files_size, files.r2_path AS files_r2_path, files.layout_json_path AS files_layout_json_path, files.status AS files_status, files.page_count AS files_page_count, files.version AS files_version, files.is_agent_written AS files_is_agent_written, files.created_at AS files_created_at, files.updated_at AS files_updated_at 
FROM files 
WHERE files.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT files.id AS files_id, files.bucket_id AS files_bucket_id, files.user_id AS files_user_id, files.category_id AS files_category_id, files.name AS files_name, files.type AS files_type, files.size AS files_size, files.r2_path AS files_r2_path, files.layout_json_path AS files_layout_json_path, files.status AS files_status, files.page_count AS files_page_count, files.version AS files_version, files.is_agent_written AS files_is_agent_written, files.created_at AS files_created_at, files.updated_at AS files_updated_at 
FROM files 
WHERE files.id = $1::UUID
2026-04-06 02:19:47,248 INFO sqlalchemy.engine.Engine [cached since 321.4s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
INFO      sqlalchemy.engine.Engine                  [cached since 321.4s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
2026-04-06 02:19:47,251 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:19:47,254 INFO sqlalchemy.engine.Engine SELECT investigation_events.id, investigation_events.file_id, investigation_events.event, investigation_events.status, investigation_events.metadata, investigation_events.created_at 
FROM investigation_events 
WHERE investigation_events.file_id = $1::UUID ORDER BY investigation_events.created_at ASC, investigation_events.event ASC
INFO      sqlalchemy.engine.Engine                  SELECT investigation_events.id, investigation_events.file_id, investigation_events.event, investigation_events.status, investigation_events.metadata, investigation_events.created_at 
FROM investigation_events 
WHERE investigation_events.file_id = $1::UUID ORDER BY investigation_events.created_at ASC, investigation_events.event ASC
2026-04-06 02:19:47,255 INFO sqlalchemy.engine.Engine [cached since 27.21s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
INFO      sqlalchemy.engine.Engine                  [cached since 27.21s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
2026-04-06 02:19:47,260 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:19:49,269 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:19:49,270 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:19:49,271 INFO sqlalchemy.engine.Engine [cached since 338.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 338.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:19:49,274 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
2026-04-06 02:19:49,275 INFO sqlalchemy.engine.Engine [cached since 338s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 338s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:19:49,278 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:19:49,790 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:19:49,792 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:19:49,793 INFO sqlalchemy.engine.Engine [cached since 338.6s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 338.6s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:19:49,795 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:19:49,796 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:19:49,797 INFO sqlalchemy.engine.Engine [cached since 338.6s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 338.6s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:19:49,800 INFO sqlalchemy.engine.Engine SELECT files.id AS files_id, files.bucket_id AS files_bucket_id, files.user_id AS files_user_id, files.category_id AS files_category_id, files.name AS files_name, files.type AS files_type, files.size AS files_size, files.r2_path AS files_r2_path, files.layout_json_path AS files_layout_json_path, files.status AS files_status, files.page_count AS files_page_count, files.version AS files_version, files.is_agent_written AS files_is_agent_written, files.created_at AS files_created_at, files.updated_at AS files_updated_at 
FROM files 
WHERE files.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT files.id AS files_id, files.bucket_id AS files_bucket_id, files.user_id AS files_user_id, files.category_id AS files_category_id, files.name AS files_name, files.type AS files_type, files.size AS files_size, files.r2_path AS files_r2_path, files.layout_json_path AS files_layout_json_path, files.status AS files_status, files.page_count AS files_page_count, files.version AS files_version, files.is_agent_written AS files_is_agent_written, files.created_at AS files_created_at, files.updated_at AS files_updated_at 
FROM files 
WHERE files.id = $1::UUID
2026-04-06 02:19:49,801 INFO sqlalchemy.engine.Engine [cached since 324s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
INFO      sqlalchemy.engine.Engine                  [cached since 324s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
2026-04-06 02:19:49,804 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:19:49,806 INFO sqlalchemy.engine.Engine SELECT files.id AS files_id, files.bucket_id AS files_bucket_id, files.user_id AS files_user_id, files.category_id AS files_category_id, files.name AS files_name, files.type AS files_type, files.size AS files_size, files.r2_path AS files_r2_path, files.layout_json_path AS files_layout_json_path, files.status AS files_status, files.page_count AS files_page_count, files.version AS files_version, files.is_agent_written AS files_is_agent_written, files.created_at AS files_created_at, files.updated_at AS files_updated_at 
FROM files 
WHERE files.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT files.id AS files_id, files.bucket_id AS files_bucket_id, files.user_id AS files_user_id, files.category_id AS files_category_id, files.name AS files_name, files.type AS files_type, files.size AS files_size, files.r2_path AS files_r2_path, files.layout_json_path AS files_layout_json_path, files.status AS files_status, files.page_count AS files_page_count, files.version AS files_version, files.is_agent_written AS files_is_agent_written, files.created_at AS files_created_at, files.updated_at AS files_updated_at 
FROM files 
WHERE files.id = $1::UUID
2026-04-06 02:19:49,807 INFO sqlalchemy.engine.Engine [cached since 324s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
INFO      sqlalchemy.engine.Engine                  [cached since 324s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
2026-04-06 02:19:49,812 INFO sqlalchemy.engine.Engine SELECT investigation_events.id, investigation_events.file_id, investigation_events.event, investigation_events.status, investigation_events.metadata, investigation_events.created_at 
FROM investigation_events 
WHERE investigation_events.file_id = $1::UUID ORDER BY investigation_events.created_at ASC, investigation_events.event ASC
INFO      sqlalchemy.engine.Engine                  SELECT investigation_events.id, investigation_events.file_id, investigation_events.event, investigation_events.status, investigation_events.metadata, investigation_events.created_at 
FROM investigation_events 
WHERE investigation_events.file_id = $1::UUID ORDER BY investigation_events.created_at ASC, investigation_events.event ASC
2026-04-06 02:19:49,813 INFO sqlalchemy.engine.Engine [cached since 29.76s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
INFO      sqlalchemy.engine.Engine                  [cached since 29.76s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
2026-04-06 02:19:49,818 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:19:52,457 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:19:52,458 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:19:52,458 INFO sqlalchemy.engine.Engine [cached since 341.3s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 341.3s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:19:52,462 INFO sqlalchemy.engine.Engine SELECT files.id AS files_id, files.bucket_id AS files_bucket_id, files.user_id AS files_user_id, files.category_id AS files_category_id, files.name AS files_name, files.type AS files_type, files.size AS files_size, files.r2_path AS files_r2_path, files.layout_json_path AS files_layout_json_path, files.status AS files_status, files.page_count AS files_page_count, files.version AS files_version, files.is_agent_written AS files_is_agent_written, files.created_at AS files_created_at, files.updated_at AS files_updated_at 
FROM files 
WHERE files.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT files.id AS files_id, files.bucket_id AS files_bucket_id, files.user_id AS files_user_id, files.category_id AS files_category_id, files.name AS files_name, files.type AS files_type, files.size AS files_size, files.r2_path AS files_r2_path, files.layout_json_path AS files_layout_json_path, files.status AS files_status, files.page_count AS files_page_count, files.version AS files_version, files.is_agent_written AS files_is_agent_written, files.created_at AS files_created_at, files.updated_at AS files_updated_at 
FROM files 
WHERE files.id = $1::UUID
2026-04-06 02:19:52,462 INFO sqlalchemy.engine.Engine [cached since 326.7s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
INFO      sqlalchemy.engine.Engine                  [cached since 326.7s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
2026-04-06 02:19:52,463 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:19:52,464 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:19:52,465 INFO sqlalchemy.engine.Engine [cached since 341.3s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 341.3s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:19:52,468 INFO sqlalchemy.engine.Engine SELECT investigation_events.id, investigation_events.file_id, investigation_events.event, investigation_events.status, investigation_events.metadata, investigation_events.created_at 
FROM investigation_events 
WHERE investigation_events.file_id = $1::UUID ORDER BY investigation_events.created_at ASC, investigation_events.event ASC
INFO      sqlalchemy.engine.Engine                  SELECT investigation_events.id, investigation_events.file_id, investigation_events.event, investigation_events.status, investigation_events.metadata, investigation_events.created_at 
FROM investigation_events 
WHERE investigation_events.file_id = $1::UUID ORDER BY investigation_events.created_at ASC, investigation_events.event ASC
2026-04-06 02:19:52,468 INFO sqlalchemy.engine.Engine [cached since 32.42s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
INFO      sqlalchemy.engine.Engine                  [cached since 32.42s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
2026-04-06 02:19:52,472 INFO sqlalchemy.engine.Engine SELECT files.id AS files_id, files.bucket_id AS files_bucket_id, files.user_id AS files_user_id, files.category_id AS files_category_id, files.name AS files_name, files.type AS files_type, files.size AS files_size, files.r2_path AS files_r2_path, files.layout_json_path AS files_layout_json_path, files.status AS files_status, files.page_count AS files_page_count, files.version AS files_version, files.is_agent_written AS files_is_agent_written, files.created_at AS files_created_at, files.updated_at AS files_updated_at 
FROM files 
WHERE files.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT files.id AS files_id, files.bucket_id AS files_bucket_id, files.user_id AS files_user_id, files.category_id AS files_category_id, files.name AS files_name, files.type AS files_type, files.size AS files_size, files.r2_path AS files_r2_path, files.layout_json_path AS files_layout_json_path, files.status AS files_status, files.page_count AS files_page_count, files.version AS files_version, files.is_agent_written AS files_is_agent_written, files.created_at AS files_created_at, files.updated_at AS files_updated_at 
FROM files 
WHERE files.id = $1::UUID
2026-04-06 02:19:52,472 INFO sqlalchemy.engine.Engine [cached since 326.7s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
INFO      sqlalchemy.engine.Engine                  [cached since 326.7s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
2026-04-06 02:19:52,475 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:19:52,479 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:19:54,271 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:19:54,272 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:19:54,272 INFO sqlalchemy.engine.Engine [cached since 343.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 343.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:19:54,275 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
2026-04-06 02:19:54,275 INFO sqlalchemy.engine.Engine [cached since 343s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 343s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:19:54,278 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:19:55,006 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:19:55,007 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:19:55,008 INFO sqlalchemy.engine.Engine [cached since 343.8s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 343.8s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:19:55,012 INFO sqlalchemy.engine.Engine SELECT files.id AS files_id, files.bucket_id AS files_bucket_id, files.user_id AS files_user_id, files.category_id AS files_category_id, files.name AS files_name, files.type AS files_type, files.size AS files_size, files.r2_path AS files_r2_path, files.layout_json_path AS files_layout_json_path, files.status AS files_status, files.page_count AS files_page_count, files.version AS files_version, files.is_agent_written AS files_is_agent_written, files.created_at AS files_created_at, files.updated_at AS files_updated_at 
FROM files 
WHERE files.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT files.id AS files_id, files.bucket_id AS files_bucket_id, files.user_id AS files_user_id, files.category_id AS files_category_id, files.name AS files_name, files.type AS files_type, files.size AS files_size, files.r2_path AS files_r2_path, files.layout_json_path AS files_layout_json_path, files.status AS files_status, files.page_count AS files_page_count, files.version AS files_version, files.is_agent_written AS files_is_agent_written, files.created_at AS files_created_at, files.updated_at AS files_updated_at 
FROM files 
WHERE files.id = $1::UUID
2026-04-06 02:19:55,013 INFO sqlalchemy.engine.Engine [cached since 329.2s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
INFO      sqlalchemy.engine.Engine                  [cached since 329.2s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
2026-04-06 02:19:55,014 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:19:55,015 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:19:55,016 INFO sqlalchemy.engine.Engine [cached since 343.8s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 343.8s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:19:55,019 INFO sqlalchemy.engine.Engine SELECT investigation_events.id, investigation_events.file_id, investigation_events.event, investigation_events.status, investigation_events.metadata, investigation_events.created_at 
FROM investigation_events 
WHERE investigation_events.file_id = $1::UUID ORDER BY investigation_events.created_at ASC, investigation_events.event ASC
INFO      sqlalchemy.engine.Engine                  SELECT investigation_events.id, investigation_events.file_id, investigation_events.event, investigation_events.status, investigation_events.metadata, investigation_events.created_at 
FROM investigation_events 
WHERE investigation_events.file_id = $1::UUID ORDER BY investigation_events.created_at ASC, investigation_events.event ASC
2026-04-06 02:19:55,020 INFO sqlalchemy.engine.Engine [cached since 34.97s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
INFO      sqlalchemy.engine.Engine                  [cached since 34.97s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
2026-04-06 02:19:55,025 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:19:55,028 INFO sqlalchemy.engine.Engine SELECT files.id AS files_id, files.bucket_id AS files_bucket_id, files.user_id AS files_user_id, files.category_id AS files_category_id, files.name AS files_name, files.type AS files_type, files.size AS files_size, files.r2_path AS files_r2_path, files.layout_json_path AS files_layout_json_path, files.status AS files_status, files.page_count AS files_page_count, files.version AS files_version, files.is_agent_written AS files_is_agent_written, files.created_at AS files_created_at, files.updated_at AS files_updated_at 
FROM files 
WHERE files.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT files.id AS files_id, files.bucket_id AS files_bucket_id, files.user_id AS files_user_id, files.category_id AS files_category_id, files.name AS files_name, files.type AS files_type, files.size AS files_size, files.r2_path AS files_r2_path, files.layout_json_path AS files_layout_json_path, files.status AS files_status, files.page_count AS files_page_count, files.version AS files_version, files.is_agent_written AS files_is_agent_written, files.created_at AS files_created_at, files.updated_at AS files_updated_at 
FROM files 
WHERE files.id = $1::UUID
2026-04-06 02:19:55,029 INFO sqlalchemy.engine.Engine [cached since 329.2s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
INFO      sqlalchemy.engine.Engine                  [cached since 329.2s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
2026-04-06 02:19:55,031 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:19:57,567 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:19:57,568 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:19:57,569 INFO sqlalchemy.engine.Engine [cached since 346.4s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 346.4s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:19:57,701 INFO sqlalchemy.engine.Engine SELECT files.id AS files_id, files.bucket_id AS files_bucket_id, files.user_id AS files_user_id, files.category_id AS files_category_id, files.name AS files_name, files.type AS files_type, files.size AS files_size, files.r2_path AS files_r2_path, files.layout_json_path AS files_layout_json_path, files.status AS files_status, files.page_count AS files_page_count, files.version AS files_version, files.is_agent_written AS files_is_agent_written, files.created_at AS files_created_at, files.updated_at AS files_updated_at 
FROM files 
WHERE files.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT files.id AS files_id, files.bucket_id AS files_bucket_id, files.user_id AS files_user_id, files.category_id AS files_category_id, files.name AS files_name, files.type AS files_type, files.size AS files_size, files.r2_path AS files_r2_path, files.layout_json_path AS files_layout_json_path, files.status AS files_status, files.page_count AS files_page_count, files.version AS files_version, files.is_agent_written AS files_is_agent_written, files.created_at AS files_created_at, files.updated_at AS files_updated_at 
FROM files 
WHERE files.id = $1::UUID
2026-04-06 02:19:57,702 INFO sqlalchemy.engine.Engine [cached since 331.9s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
INFO      sqlalchemy.engine.Engine                  [cached since 331.9s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
2026-04-06 02:19:57,704 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:19:57,706 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:19:57,707 INFO sqlalchemy.engine.Engine [cached since 346.5s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 346.5s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:19:57,710 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:19:57,714 INFO sqlalchemy.engine.Engine SELECT files.id AS files_id, files.bucket_id AS files_bucket_id, files.user_id AS files_user_id, files.category_id AS files_category_id, files.name AS files_name, files.type AS files_type, files.size AS files_size, files.r2_path AS files_r2_path, files.layout_json_path AS files_layout_json_path, files.status AS files_status, files.page_count AS files_page_count, files.version AS files_version, files.is_agent_written AS files_is_agent_written, files.created_at AS files_created_at, files.updated_at AS files_updated_at 
FROM files 
WHERE files.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT files.id AS files_id, files.bucket_id AS files_bucket_id, files.user_id AS files_user_id, files.category_id AS files_category_id, files.name AS files_name, files.type AS files_type, files.size AS files_size, files.r2_path AS files_r2_path, files.layout_json_path AS files_layout_json_path, files.status AS files_status, files.page_count AS files_page_count, files.version AS files_version, files.is_agent_written AS files_is_agent_written, files.created_at AS files_created_at, files.updated_at AS files_updated_at 
FROM files 
WHERE files.id = $1::UUID
2026-04-06 02:19:57,715 INFO sqlalchemy.engine.Engine [cached since 331.9s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
INFO      sqlalchemy.engine.Engine                  [cached since 331.9s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
2026-04-06 02:19:57,718 INFO sqlalchemy.engine.Engine SELECT investigation_events.id, investigation_events.file_id, investigation_events.event, investigation_events.status, investigation_events.metadata, investigation_events.created_at 
FROM investigation_events 
WHERE investigation_events.file_id = $1::UUID ORDER BY investigation_events.created_at ASC, investigation_events.event ASC
INFO      sqlalchemy.engine.Engine                  SELECT investigation_events.id, investigation_events.file_id, investigation_events.event, investigation_events.status, investigation_events.metadata, investigation_events.created_at 
FROM investigation_events 
WHERE investigation_events.file_id = $1::UUID ORDER BY investigation_events.created_at ASC, investigation_events.event ASC
2026-04-06 02:19:57,719 INFO sqlalchemy.engine.Engine [cached since 37.67s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
INFO      sqlalchemy.engine.Engine                  [cached since 37.67s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
2026-04-06 02:19:57,725 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:19:59,271 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:19:59,272 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:19:59,272 INFO sqlalchemy.engine.Engine [cached since 348.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 348.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:19:59,276 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
2026-04-06 02:19:59,277 INFO sqlalchemy.engine.Engine [cached since 348.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 348.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:19:59,280 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:20:00,258 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:20:00,259 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:20:00,260 INFO sqlalchemy.engine.Engine [cached since 349.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 349.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:20:00,263 INFO sqlalchemy.engine.Engine SELECT files.id AS files_id, files.bucket_id AS files_bucket_id, files.user_id AS files_user_id, files.category_id AS files_category_id, files.name AS files_name, files.type AS files_type, files.size AS files_size, files.r2_path AS files_r2_path, files.layout_json_path AS files_layout_json_path, files.status AS files_status, files.page_count AS files_page_count, files.version AS files_version, files.is_agent_written AS files_is_agent_written, files.created_at AS files_created_at, files.updated_at AS files_updated_at 
FROM files 
WHERE files.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT files.id AS files_id, files.bucket_id AS files_bucket_id, files.user_id AS files_user_id, files.category_id AS files_category_id, files.name AS files_name, files.type AS files_type, files.size AS files_size, files.r2_path AS files_r2_path, files.layout_json_path AS files_layout_json_path, files.status AS files_status, files.page_count AS files_page_count, files.version AS files_version, files.is_agent_written AS files_is_agent_written, files.created_at AS files_created_at, files.updated_at AS files_updated_at 
FROM files 
WHERE files.id = $1::UUID
2026-04-06 02:20:00,264 INFO sqlalchemy.engine.Engine [cached since 334.5s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
INFO      sqlalchemy.engine.Engine                  [cached since 334.5s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
2026-04-06 02:20:00,267 INFO sqlalchemy.engine.Engine SELECT investigation_events.id, investigation_events.file_id, investigation_events.event, investigation_events.status, investigation_events.metadata, investigation_events.created_at 
FROM investigation_events 
WHERE investigation_events.file_id = $1::UUID ORDER BY investigation_events.created_at ASC, investigation_events.event ASC
INFO      sqlalchemy.engine.Engine                  SELECT investigation_events.id, investigation_events.file_id, investigation_events.event, investigation_events.status, investigation_events.metadata, investigation_events.created_at 
FROM investigation_events 
WHERE investigation_events.file_id = $1::UUID ORDER BY investigation_events.created_at ASC, investigation_events.event ASC
2026-04-06 02:20:00,267 INFO sqlalchemy.engine.Engine [cached since 40.22s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
INFO      sqlalchemy.engine.Engine                  [cached since 40.22s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
2026-04-06 02:20:00,271 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:20:00,273 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:20:00,274 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:20:00,274 INFO sqlalchemy.engine.Engine [cached since 349.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 349.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:20:00,277 INFO sqlalchemy.engine.Engine SELECT files.id AS files_id, files.bucket_id AS files_bucket_id, files.user_id AS files_user_id, files.category_id AS files_category_id, files.name AS files_name, files.type AS files_type, files.size AS files_size, files.r2_path AS files_r2_path, files.layout_json_path AS files_layout_json_path, files.status AS files_status, files.page_count AS files_page_count, files.version AS files_version, files.is_agent_written AS files_is_agent_written, files.created_at AS files_created_at, files.updated_at AS files_updated_at 
FROM files 
WHERE files.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT files.id AS files_id, files.bucket_id AS files_bucket_id, files.user_id AS files_user_id, files.category_id AS files_category_id, files.name AS files_name, files.type AS files_type, files.size AS files_size, files.r2_path AS files_r2_path, files.layout_json_path AS files_layout_json_path, files.status AS files_status, files.page_count AS files_page_count, files.version AS files_version, files.is_agent_written AS files_is_agent_written, files.created_at AS files_created_at, files.updated_at AS files_updated_at 
FROM files 
WHERE files.id = $1::UUID
2026-04-06 02:20:00,278 INFO sqlalchemy.engine.Engine [cached since 334.5s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
INFO      sqlalchemy.engine.Engine                  [cached since 334.5s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
2026-04-06 02:20:00,281 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:20:02,817 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:20:02,819 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:20:02,820 INFO sqlalchemy.engine.Engine [cached since 351.6s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 351.6s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:20:02,824 INFO sqlalchemy.engine.Engine SELECT files.id AS files_id, files.bucket_id AS files_bucket_id, files.user_id AS files_user_id, files.category_id AS files_category_id, files.name AS files_name, files.type AS files_type, files.size AS files_size, files.r2_path AS files_r2_path, files.layout_json_path AS files_layout_json_path, files.status AS files_status, files.page_count AS files_page_count, files.version AS files_version, files.is_agent_written AS files_is_agent_written, files.created_at AS files_created_at, files.updated_at AS files_updated_at 
FROM files 
WHERE files.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT files.id AS files_id, files.bucket_id AS files_bucket_id, files.user_id AS files_user_id, files.category_id AS files_category_id, files.name AS files_name, files.type AS files_type, files.size AS files_size, files.r2_path AS files_r2_path, files.layout_json_path AS files_layout_json_path, files.status AS files_status, files.page_count AS files_page_count, files.version AS files_version, files.is_agent_written AS files_is_agent_written, files.created_at AS files_created_at, files.updated_at AS files_updated_at 
FROM files 
WHERE files.id = $1::UUID
2026-04-06 02:20:02,949 INFO sqlalchemy.engine.Engine [cached since 337.1s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
INFO      sqlalchemy.engine.Engine                  [cached since 337.1s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
2026-04-06 02:20:02,950 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:20:02,951 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:20:02,952 INFO sqlalchemy.engine.Engine [cached since 351.7s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 351.7s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:20:02,955 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:20:02,958 INFO sqlalchemy.engine.Engine SELECT files.id AS files_id, files.bucket_id AS files_bucket_id, files.user_id AS files_user_id, files.category_id AS files_category_id, files.name AS files_name, files.type AS files_type, files.size AS files_size, files.r2_path AS files_r2_path, files.layout_json_path AS files_layout_json_path, files.status AS files_status, files.page_count AS files_page_count, files.version AS files_version, files.is_agent_written AS files_is_agent_written, files.created_at AS files_created_at, files.updated_at AS files_updated_at 
FROM files 
WHERE files.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT files.id AS files_id, files.bucket_id AS files_bucket_id, files.user_id AS files_user_id, files.category_id AS files_category_id, files.name AS files_name, files.type AS files_type, files.size AS files_size, files.r2_path AS files_r2_path, files.layout_json_path AS files_layout_json_path, files.status AS files_status, files.page_count AS files_page_count, files.version AS files_version, files.is_agent_written AS files_is_agent_written, files.created_at AS files_created_at, files.updated_at AS files_updated_at 
FROM files 
WHERE files.id = $1::UUID
2026-04-06 02:20:02,959 INFO sqlalchemy.engine.Engine [cached since 337.2s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
INFO      sqlalchemy.engine.Engine                  [cached since 337.2s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
2026-04-06 02:20:02,962 INFO sqlalchemy.engine.Engine SELECT investigation_events.id, investigation_events.file_id, investigation_events.event, investigation_events.status, investigation_events.metadata, investigation_events.created_at 
FROM investigation_events 
WHERE investigation_events.file_id = $1::UUID ORDER BY investigation_events.created_at ASC, investigation_events.event ASC
INFO      sqlalchemy.engine.Engine                  SELECT investigation_events.id, investigation_events.file_id, investigation_events.event, investigation_events.status, investigation_events.metadata, investigation_events.created_at 
FROM investigation_events 
WHERE investigation_events.file_id = $1::UUID ORDER BY investigation_events.created_at ASC, investigation_events.event ASC
2026-04-06 02:20:02,963 INFO sqlalchemy.engine.Engine [cached since 42.91s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
INFO      sqlalchemy.engine.Engine                  [cached since 42.91s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
2026-04-06 02:20:02,967 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:20:04,274 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:20:04,275 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:20:04,275 INFO sqlalchemy.engine.Engine [cached since 353.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 353.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:20:04,279 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
2026-04-06 02:20:04,279 INFO sqlalchemy.engine.Engine [cached since 353.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 353.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:20:04,281 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:20:05,504 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:20:05,505 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:20:05,506 INFO sqlalchemy.engine.Engine [cached since 354.3s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 354.3s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:20:05,510 INFO sqlalchemy.engine.Engine SELECT files.id AS files_id, files.bucket_id AS files_bucket_id, files.user_id AS files_user_id, files.category_id AS files_category_id, files.name AS files_name, files.type AS files_type, files.size AS files_size, files.r2_path AS files_r2_path, files.layout_json_path AS files_layout_json_path, files.status AS files_status, files.page_count AS files_page_count, files.version AS files_version, files.is_agent_written AS files_is_agent_written, files.created_at AS files_created_at, files.updated_at AS files_updated_at 
FROM files 
WHERE files.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT files.id AS files_id, files.bucket_id AS files_bucket_id, files.user_id AS files_user_id, files.category_id AS files_category_id, files.name AS files_name, files.type AS files_type, files.size AS files_size, files.r2_path AS files_r2_path, files.layout_json_path AS files_layout_json_path, files.status AS files_status, files.page_count AS files_page_count, files.version AS files_version, files.is_agent_written AS files_is_agent_written, files.created_at AS files_created_at, files.updated_at AS files_updated_at 
FROM files 
WHERE files.id = $1::UUID
2026-04-06 02:20:05,511 INFO sqlalchemy.engine.Engine [cached since 339.7s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
INFO      sqlalchemy.engine.Engine                  [cached since 339.7s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
2026-04-06 02:20:05,513 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:20:05,515 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:20:05,516 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:20:05,517 INFO sqlalchemy.engine.Engine [cached since 354.3s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 354.3s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:20:05,521 INFO sqlalchemy.engine.Engine SELECT files.id AS files_id, files.bucket_id AS files_bucket_id, files.user_id AS files_user_id, files.category_id AS files_category_id, files.name AS files_name, files.type AS files_type, files.size AS files_size, files.r2_path AS files_r2_path, files.layout_json_path AS files_layout_json_path, files.status AS files_status, files.page_count AS files_page_count, files.version AS files_version, files.is_agent_written AS files_is_agent_written, files.created_at AS files_created_at, files.updated_at AS files_updated_at 
FROM files 
WHERE files.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT files.id AS files_id, files.bucket_id AS files_bucket_id, files.user_id AS files_user_id, files.category_id AS files_category_id, files.name AS files_name, files.type AS files_type, files.size AS files_size, files.r2_path AS files_r2_path, files.layout_json_path AS files_layout_json_path, files.status AS files_status, files.page_count AS files_page_count, files.version AS files_version, files.is_agent_written AS files_is_agent_written, files.created_at AS files_created_at, files.updated_at AS files_updated_at 
FROM files 
WHERE files.id = $1::UUID
2026-04-06 02:20:05,522 INFO sqlalchemy.engine.Engine [cached since 339.7s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
INFO      sqlalchemy.engine.Engine                  [cached since 339.7s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
2026-04-06 02:20:05,525 INFO sqlalchemy.engine.Engine SELECT investigation_events.id, investigation_events.file_id, investigation_events.event, investigation_events.status, investigation_events.metadata, investigation_events.created_at 
FROM investigation_events 
WHERE investigation_events.file_id = $1::UUID ORDER BY investigation_events.created_at ASC, investigation_events.event ASC
INFO      sqlalchemy.engine.Engine                  SELECT investigation_events.id, investigation_events.file_id, investigation_events.event, investigation_events.status, investigation_events.metadata, investigation_events.created_at 
FROM investigation_events 
WHERE investigation_events.file_id = $1::UUID ORDER BY investigation_events.created_at ASC, investigation_events.event ASC
2026-04-06 02:20:05,527 INFO sqlalchemy.engine.Engine [cached since 45.48s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
INFO      sqlalchemy.engine.Engine                  [cached since 45.48s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
2026-04-06 02:20:05,532 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:20:08,070 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:20:08,070 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:20:08,071 INFO sqlalchemy.engine.Engine [cached since 356.9s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 356.9s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:20:08,072 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:20:08,073 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:20:08,199 INFO sqlalchemy.engine.Engine [cached since 357s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 357s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:20:08,203 INFO sqlalchemy.engine.Engine SELECT files.id AS files_id, files.bucket_id AS files_bucket_id, files.user_id AS files_user_id, files.category_id AS files_category_id, files.name AS files_name, files.type AS files_type, files.size AS files_size, files.r2_path AS files_r2_path, files.layout_json_path AS files_layout_json_path, files.status AS files_status, files.page_count AS files_page_count, files.version AS files_version, files.is_agent_written AS files_is_agent_written, files.created_at AS files_created_at, files.updated_at AS files_updated_at 
FROM files 
WHERE files.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT files.id AS files_id, files.bucket_id AS files_bucket_id, files.user_id AS files_user_id, files.category_id AS files_category_id, files.name AS files_name, files.type AS files_type, files.size AS files_size, files.r2_path AS files_r2_path, files.layout_json_path AS files_layout_json_path, files.status AS files_status, files.page_count AS files_page_count, files.version AS files_version, files.is_agent_written AS files_is_agent_written, files.created_at AS files_created_at, files.updated_at AS files_updated_at 
FROM files 
WHERE files.id = $1::UUID
2026-04-06 02:20:08,204 INFO sqlalchemy.engine.Engine [cached since 342.4s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
INFO      sqlalchemy.engine.Engine                  [cached since 342.4s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
2026-04-06 02:20:08,206 INFO sqlalchemy.engine.Engine SELECT files.id AS files_id, files.bucket_id AS files_bucket_id, files.user_id AS files_user_id, files.category_id AS files_category_id, files.name AS files_name, files.type AS files_type, files.size AS files_size, files.r2_path AS files_r2_path, files.layout_json_path AS files_layout_json_path, files.status AS files_status, files.page_count AS files_page_count, files.version AS files_version, files.is_agent_written AS files_is_agent_written, files.created_at AS files_created_at, files.updated_at AS files_updated_at 
FROM files 
WHERE files.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT files.id AS files_id, files.bucket_id AS files_bucket_id, files.user_id AS files_user_id, files.category_id AS files_category_id, files.name AS files_name, files.type AS files_type, files.size AS files_size, files.r2_path AS files_r2_path, files.layout_json_path AS files_layout_json_path, files.status AS files_status, files.page_count AS files_page_count, files.version AS files_version, files.is_agent_written AS files_is_agent_written, files.created_at AS files_created_at, files.updated_at AS files_updated_at 
FROM files 
WHERE files.id = $1::UUID
2026-04-06 02:20:08,207 INFO sqlalchemy.engine.Engine [cached since 342.4s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
INFO      sqlalchemy.engine.Engine                  [cached since 342.4s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
2026-04-06 02:20:08,210 INFO sqlalchemy.engine.Engine SELECT investigation_events.id, investigation_events.file_id, investigation_events.event, investigation_events.status, investigation_events.metadata, investigation_events.created_at 
FROM investigation_events 
WHERE investigation_events.file_id = $1::UUID ORDER BY investigation_events.created_at ASC, investigation_events.event ASC
INFO      sqlalchemy.engine.Engine                  SELECT investigation_events.id, investigation_events.file_id, investigation_events.event, investigation_events.status, investigation_events.metadata, investigation_events.created_at 
FROM investigation_events 
WHERE investigation_events.file_id = $1::UUID ORDER BY investigation_events.created_at ASC, investigation_events.event ASC
2026-04-06 02:20:08,210 INFO sqlalchemy.engine.Engine [cached since 48.16s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
INFO      sqlalchemy.engine.Engine                  [cached since 48.16s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
2026-04-06 02:20:08,212 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:20:08,217 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:20:09,268 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:20:09,269 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:20:09,269 INFO sqlalchemy.engine.Engine [cached since 358.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 358.1s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:20:09,273 INFO sqlalchemy.engine.Engine SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
INFO      sqlalchemy.engine.Engine                  SELECT files.id, files.bucket_id, files.user_id, files.category_id, files.name, files.type, files.size, files.r2_path, files.layout_json_path, files.status, files.page_count, files.version, files.is_agent_written, files.created_at, files.updated_at 
FROM files 
WHERE files.bucket_id = $1::UUID ORDER BY files.created_at DESC
2026-04-06 02:20:09,273 INFO sqlalchemy.engine.Engine [cached since 358s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 358s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:20:09,276 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:20:10,754 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:20:10,754 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:20:10,755 INFO sqlalchemy.engine.Engine [cached since 359.6s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 359.6s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:20:10,758 INFO sqlalchemy.engine.Engine SELECT files.id AS files_id, files.bucket_id AS files_bucket_id, files.user_id AS files_user_id, files.category_id AS files_category_id, files.name AS files_name, files.type AS files_type, files.size AS files_size, files.r2_path AS files_r2_path, files.layout_json_path AS files_layout_json_path, files.status AS files_status, files.page_count AS files_page_count, files.version AS files_version, files.is_agent_written AS files_is_agent_written, files.created_at AS files_created_at, files.updated_at AS files_updated_at 
FROM files 
WHERE files.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT files.id AS files_id, files.bucket_id AS files_bucket_id, files.user_id AS files_user_id, files.category_id AS files_category_id, files.name AS files_name, files.type AS files_type, files.size AS files_size, files.r2_path AS files_r2_path, files.layout_json_path AS files_layout_json_path, files.status AS files_status, files.page_count AS files_page_count, files.version AS files_version, files.is_agent_written AS files_is_agent_written, files.created_at AS files_created_at, files.updated_at AS files_updated_at 
FROM files 
WHERE files.id = $1::UUID
2026-04-06 02:20:10,758 INFO sqlalchemy.engine.Engine [cached since 345s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
INFO      sqlalchemy.engine.Engine                  [cached since 345s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
2026-04-06 02:20:10,760 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2026-04-06 02:20:10,762 INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO      sqlalchemy.engine.Engine                  BEGIN (implicit)
2026-04-06 02:20:10,763 INFO sqlalchemy.engine.Engine SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT buckets.id AS buckets_id, buckets.user_id AS buckets_user_id, buckets.name AS buckets_name, buckets.description AS buckets_description, buckets.mcp_url AS buckets_mcp_url, buckets.mcp_token AS buckets_mcp_token, buckets.account_mcp_url AS buckets_account_mcp_url, buckets.account_mcp_token AS buckets_account_mcp_token, buckets.color AS buckets_color, buckets.icon AS buckets_icon, buckets.is_public AS buckets_is_public, buckets.storage_used AS buckets_storage_used, buckets.created_at AS buckets_created_at, buckets.updated_at AS buckets_updated_at 
FROM buckets 
WHERE buckets.id = $1::UUID
2026-04-06 02:20:10,763 INFO sqlalchemy.engine.Engine [cached since 359.6s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
INFO      sqlalchemy.engine.Engine                  [cached since 359.6s ago] (UUID('cda93db7-ec50-409c-95d5-8eddafe391ac'),)
2026-04-06 02:20:10,766 INFO sqlalchemy.engine.Engine SELECT files.id AS files_id, files.bucket_id AS files_bucket_id, files.user_id AS files_user_id, files.category_id AS files_category_id, files.name AS files_name, files.type AS files_type, files.size AS files_size, files.r2_path AS files_r2_path, files.layout_json_path AS files_layout_json_path, files.status AS files_status, files.page_count AS files_page_count, files.version AS files_version, files.is_agent_written AS files_is_agent_written, files.created_at AS files_created_at, files.updated_at AS files_updated_at 
FROM files 
WHERE files.id = $1::UUID
INFO      sqlalchemy.engine.Engine                  SELECT files.id AS files_id, files.bucket_id AS files_bucket_id, files.user_id AS files_user_id, files.category_id AS files_category_id, files.name AS files_name, files.type AS files_type, files.size AS files_size, files.r2_path AS files_r2_path, files.layout_json_path AS files_layout_json_path, files.status AS files_status, files.page_count AS files_page_count, files.version AS files_version, files.is_agent_written AS files_is_agent_written, files.created_at AS files_created_at, files.updated_at AS files_updated_at 
FROM files 
WHERE files.id = $1::UUID
2026-04-06 02:20:10,767 INFO sqlalchemy.engine.Engine [cached since 345s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
INFO      sqlalchemy.engine.Engine                  [cached since 345s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
2026-04-06 02:20:10,770 INFO sqlalchemy.engine.Engine SELECT investigation_events.id, investigation_events.file_id, investigation_events.event, investigation_events.status, investigation_events.metadata, investigation_events.created_at 
FROM investigation_events 
WHERE investigation_events.file_id = $1::UUID ORDER BY investigation_events.created_at ASC, investigation_events.event ASC
INFO      sqlalchemy.engine.Engine                  SELECT investigation_events.id, investigation_events.file_id, investigation_events.event, investigation_events.status, investigation_events.metadata, investigation_events.created_at 
FROM investigation_events 
WHERE investigation_events.file_id = $1::UUID ORDER BY investigation_events.created_at ASC, investigation_events.event ASC
2026-04-06 02:20:10,771 INFO sqlalchemy.engine.Engine [cached since 50.72s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
INFO      sqlalchemy.engine.Engine                  [cached since 50.72s ago] (UUID('1fbb1f0f-eeb1-49fb-b4ae-f7db9dbb96c7'),)
2026-04-06 02:20:10,775 INFO sqlalchemy.engine.Engine ROLLBACK
INFO      sqlalchemy.engine.Engine                  ROLLBACK
2