Last login: Thu Mar  5 00:24:25 on ttys001
You have new mail.
chaffanjutt@Affans-MacBook-Air AIveilix %  cd /Volumes/KIOXIA/AIveilix/backend && source venv/bin/activate && python run.py
INFO:     Will watch for changes in these directories: ['/Volumes/KIOXIA/AIveilix/backend']
INFO:     Uvicorn running on http://0.0.0.0:7223 (Press CTRL+C to quit)
INFO:     Started reloader process [81713] using WatchFiles
2026-03-05 23:08:36,730 - app.main - INFO - ✅ CORS allowed origins: ['https://aiveilix.com,https://aiveilix-427f3.web.app/', 'https://aiveilix.com', 'https://www.aiveilix.com', 'https://api.aiveilix.com', 'http://localhost:6677', 'http://localhost:5173', 'http://localhost:3000', 'http://127.0.0.1:6677', 'http://127.0.0.1:5173', 'https://chat.openai.com', 'https://chatgpt.com', 'https://claude.ai']
/Volumes/KIOXIA/AIveilix/backend/app/services/file_processor.py:13: FutureWarning: 

All support for the `google.generativeai` package has ended. It will no longer be receiving 
updates or bug fixes. Please switch to the `google.genai` package as soon as possible.
See README for more details:

https://github.com/google-gemini/deprecated-generative-ai-python/blob/main/README.md

  import google.generativeai as genai
2026-03-05 23:08:40,317 - app.services.file_processor - INFO - Voyage AI configured for embeddings (voyage-3-large, 1024 dims)
2026-03-05 23:08:40,317 - app.services.file_processor - INFO - gemini-2.5-flash configured for vision/image processing
2026-03-05 23:08:40,425 - app.services.stripe_service - INFO - Stripe initialized with key: sk_test_51Sw...
INFO:     Started server process [81715]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
2026-03-05 23:08:40,603 - app.main - INFO - ⏱  GET /dev/errors  →  200  8.2ms  🟢
INFO:     127.0.0.1:60668 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:08:40,609 - app.main - INFO - ⏱  GET /dev/errors  →  200  0.7ms  🟢
INFO:     127.0.0.1:60668 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
INFO:     127.0.0.1:60668 - "OPTIONS /api/notifications/unread-count HTTP/1.1" 200 OK
INFO:     127.0.0.1:60652 - "OPTIONS /api/stripe/usage HTTP/1.1" 200 OK
2026-03-05 23:08:42,634 - app.main - INFO - ⏱  GET /dev/errors  →  200  2.2ms  🟢
INFO:     127.0.0.1:60654 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:08:42,635 - app.main - INFO - ⏱  GET /dev/errors  →  200  2.2ms  🟢
INFO:     127.0.0.1:60686 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
INFO:     127.0.0.1:60689 - "OPTIONS /api/buckets/stats/dashboard HTTP/1.1" 200 OK
INFO:     127.0.0.1:60690 - "OPTIONS /api/buckets/ HTTP/1.1" 200 OK
INFO:     127.0.0.1:60692 - "OPTIONS /api/buckets/stats/activity?days=30 HTTP/1.1" 200 OK
INFO:     127.0.0.1:60654 - "OPTIONS /api/team/members HTTP/1.1" 200 OK
INFO:     127.0.0.1:60686 - "OPTIONS /api/stripe/usage HTTP/1.1" 200 OK
INFO:     127.0.0.1:60694 - "OPTIONS /api/notifications/unread-count HTTP/1.1" 200 OK
INFO:     127.0.0.1:60690 - "OPTIONS /api/buckets/stats/dashboard HTTP/1.1" 200 OK
INFO:     127.0.0.1:60696 - "OPTIONS /api/buckets/ HTTP/1.1" 200 OK
INFO:     127.0.0.1:60692 - "OPTIONS /api/buckets/stats/activity?days=30 HTTP/1.1" 200 OK
INFO:     127.0.0.1:60654 - "OPTIONS /api/team/members HTTP/1.1" 200 OK
2026-03-05 23:08:42,664 - app.main - INFO - ⏱  GET /api/notifications/unread-count  →  401  19.0ms  🟢
INFO:     127.0.0.1:60686 - "GET /api/notifications/unread-count HTTP/1.1" 401 Unauthorized
2026-03-05 23:08:42,665 - app.main - INFO - ⏱  GET /api/stripe/usage  →  401  19.3ms  🟢
INFO:     127.0.0.1:60694 - "GET /api/stripe/usage HTTP/1.1" 401 Unauthorized
2026-03-05 23:08:42,705 - app.main - INFO - ⏱  GET /api/buckets/stats/dashboard  →  401  32.8ms  🟢
INFO:     127.0.0.1:60690 - "GET /api/buckets/stats/dashboard HTTP/1.1" 401 Unauthorized
2026-03-05 23:08:42,722 - app.main - INFO - ⏱  GET /api/buckets/  →  401  16.7ms  🟢
INFO:     127.0.0.1:60698 - "GET /api/buckets/ HTTP/1.1" 401 Unauthorized
2026-03-05 23:08:42,722 - app.main - INFO - ⏱  GET /api/buckets/stats/activity  →  401  17.0ms  🟢
INFO:     127.0.0.1:60686 - "GET /api/buckets/stats/activity?days=30 HTTP/1.1" 401 Unauthorized
2026-03-05 23:08:42,723 - app.main - INFO - ⏱  GET /api/notifications/unread-count  →  401  17.4ms  🟢
INFO:     127.0.0.1:60654 - "GET /api/notifications/unread-count HTTP/1.1" 401 Unauthorized
2026-03-05 23:08:42,723 - app.main - INFO - ⏱  GET /api/team/members  →  401  17.7ms  🟢
INFO:     127.0.0.1:60694 - "GET /api/team/members HTTP/1.1" 401 Unauthorized
2026-03-05 23:08:42,723 - app.main - INFO - ⏱  GET /api/stripe/usage  →  401  2.6ms  🟢
INFO:     127.0.0.1:60700 - "GET /api/stripe/usage HTTP/1.1" 401 Unauthorized
2026-03-05 23:08:42,737 - app.main - INFO - ⏱  GET /api/buckets/  →  401  6.8ms  🟢
INFO:     127.0.0.1:60690 - "GET /api/buckets/ HTTP/1.1" 401 Unauthorized
2026-03-05 23:08:42,737 - app.main - INFO - ⏱  GET /api/buckets/stats/dashboard  →  401  7.2ms  🟢
INFO:     127.0.0.1:60698 - "GET /api/buckets/stats/dashboard HTTP/1.1" 401 Unauthorized
2026-03-05 23:08:42,738 - app.main - INFO - ⏱  GET /api/buckets/stats/activity  →  401  7.6ms  🟢
INFO:     127.0.0.1:60686 - "GET /api/buckets/stats/activity?days=30 HTTP/1.1" 401 Unauthorized
2026-03-05 23:08:42,738 - app.main - INFO - ⏱  GET /api/team/members  →  401  8.0ms  🟢
INFO:     127.0.0.1:60654 - "GET /api/team/members HTTP/1.1" 401 Unauthorized
2026-03-05 23:08:42,758 - app.main - INFO - ⏱  GET /api/buckets/stats/activity  →  401  3.0ms  🟢
INFO:     127.0.0.1:60686 - "GET /api/buckets/stats/activity?start_date=2026-02-26&end_date=2026-03-05 HTTP/1.1" 401 Unauthorized
2026-03-05 23:08:42,760 - app.main - INFO - ⏱  GET /api/buckets/stats/activity  →  401  3.0ms  🟢
INFO:     127.0.0.1:60654 - "GET /api/buckets/stats/activity?start_date=2026-02-26&end_date=2026-03-05 HTTP/1.1" 401 Unauthorized
2026-03-05 23:08:43,332 - app.main - INFO - ⏱  GET /dev/errors  →  200  2.8ms  🟢
INFO:     127.0.0.1:60654 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:08:43,332 - app.main - INFO - ⏱  GET /dev/errors  →  200  2.6ms  🟢
INFO:     127.0.0.1:60686 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:08:47,309 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.0ms  🟢
INFO:     127.0.0.1:60654 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:08:50,932 - app.main - INFO - ⏱  GET /dev/errors  →  200  0.9ms  🟢
INFO:     127.0.0.1:60654 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:08:50,935 - app.main - INFO - ⏱  GET /dev/errors  →  200  0.4ms  🟢
INFO:     127.0.0.1:60654 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:09:09,804 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.1ms  🟢
INFO:     127.0.0.1:60740 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:09:09,805 - app.main - INFO - ⏱  GET /dev/errors  →  200  0.2ms  🟢
INFO:     127.0.0.1:60740 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:09:13,809 - app.main - INFO - ⏱  GET /dev/errors  →  200  0.8ms  🟢
INFO:     127.0.0.1:60740 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:09:17,810 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.1ms  🟢
INFO:     127.0.0.1:60740 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
INFO:     127.0.0.1:60740 - "OPTIONS /api/auth/login HTTP/1.1" 200 OK
2026-03-05 23:09:18,169 - tracer - INFO - [a6592510] START POST /api/auth/login  email=chaffanjutt313@gmail.com
2026-03-05 23:09:18,170 - tracer - INFO - [a6592510]   🟢 Get supabase auth client  0.2ms (total 0.2ms)  
2026-03-05 23:09:19,509 - tracer - INFO - [a6592510]   🟡 Supabase sign_in_with_password  1339.2ms (total 1339.4ms)  
2026-03-05 23:09:19,509 - tracer - INFO - [a6592510] END POST /api/auth/login  OK 200  1339.5ms  🟡  steps=2  slowest=Supabase sign_in_with_password(1339.2ms)
2026-03-05 23:09:19,509 - app.main - WARNING - ⏱  POST /api/auth/login  →  200  1356.8ms  🟡 SLOW
INFO:     127.0.0.1:60740 - "POST /api/auth/login HTTP/1.1" 200 OK
INFO:     127.0.0.1:60740 - "OPTIONS /api/auth/me HTTP/1.1" 200 OK
2026-03-05 23:09:19,519 - tracer - INFO - [abf9664c] START GET /api/auth/me  
2026-03-05 23:09:19,713 - tracer - INFO - [abf9664c]   🟢 Supabase get_user  193.3ms (total 193.3ms)  
2026-03-05 23:09:20,289 - tracer - INFO - [abf9664c]   🟢 Team member context check  576.2ms (total 769.5ms)  
2026-03-05 23:09:20,289 - tracer - INFO - [abf9664c] END GET /api/auth/me  OK 200  769.7ms  🟢  steps=2  slowest=Team member context check(576.2ms)
2026-03-05 23:09:20,290 - app.main - INFO - ⏱  GET /api/auth/me  →  200  773.2ms  🟢
INFO:     127.0.0.1:60740 - "GET /api/auth/me HTTP/1.1" 200 OK
2026-03-05 23:09:20,664 - app.routers.stripe - INFO - [Usage] Getting usage for user=48c4c78c-bdfb-41b0-85d1-cadd60b9c555
2026-03-05 23:09:20,665 - app.main - INFO - ⏱  GET /api/notifications/unread-count  →  200  374.6ms  🟢
INFO:     127.0.0.1:60751 - "GET /api/notifications/unread-count HTTP/1.1" 200 OK
2026-03-05 23:09:20,898 - app.services.plan_limits - WARNING - [get_metric_count] chat_messages/daily: 'NoneType' object has no attribute 'data'
2026-03-05 23:09:21,088 - app.services.plan_limits - WARNING - [get_metric_count] mcp_queries/daily: 'NoneType' object has no attribute 'data'
2026-03-05 23:09:21,291 - app.services.plan_limits - WARNING - [get_metric_count] bucket_chat/daily: 'NoneType' object has no attribute 'data'
2026-03-05 23:09:21,511 - tracer - INFO - [a1e72ca4] START GET /api/buckets/stats/dashboard  user_id=48c4c78c-bdfb-41b0-85d1-cadd60b9c555
2026-03-05 23:09:21,702 - tracer - INFO - [a1e72ca4]   🟢 DB query bucket stats  190.7ms (total 190.7ms)  
2026-03-05 23:09:21,702 - tracer - INFO - [a1e72ca4] END GET /api/buckets/stats/dashboard  OK 200  191.2ms  🟢  steps=1  slowest=DB query bucket stats(190.7ms)
2026-03-05 23:09:21,712 - tracer - INFO - [c6955755] START GET /api/buckets  user_id=48c4c78c-bdfb-41b0-85d1-cadd60b9c555
2026-03-05 23:09:21,712 - tracer - INFO - [c6955755]   🟢 get_effective_user_id  0.3ms (total 0.3ms)  
2026-03-05 23:09:21,712 - tracer - INFO - [c6955755]   🟢 get_member_accessible_buckets  0.1ms (total 0.4ms)  
2026-03-05 23:09:22,261 - tracer - INFO - [c6955755]   🟢 DB query buckets  549.0ms (total 549.4ms)  count=67
2026-03-05 23:09:22,262 - tracer - INFO - [c6955755] END GET /api/buckets  OK 200  550.6ms  🟢  steps=3  slowest=DB query buckets(549.0ms)
2026-03-05 23:09:22,265 - app.main - WARNING - ⏱  GET /api/buckets/stats/dashboard  →  200  1601.0ms  🟡 SLOW
INFO:     127.0.0.1:60761 - "GET /api/buckets/stats/dashboard HTTP/1.1" 200 OK
2026-03-05 23:09:23,793 - tracer - INFO - [9000a45b] START GET /api/buckets/stats/activity  user_id=48c4c78c-bdfb-41b0-85d1-cadd60b9c555
2026-03-05 23:09:24,208 - tracer - INFO - [9000a45b]   🟢 DB query baselines  415.6ms (total 415.6ms)  
2026-03-05 23:09:24,634 - tracer - INFO - [9000a45b]   🟢 DB query range data  425.0ms (total 840.7ms)  
2026-03-05 23:09:24,635 - tracer - INFO - [9000a45b] END GET /api/buckets/stats/activity  OK 200  841.9ms  🟢  steps=2  slowest=DB query range data(425.0ms)
2026-03-05 23:09:24,636 - app.main - WARNING - ⏱  GET /api/buckets/  →  200  2933.2ms  🟡 SLOW
INFO:     127.0.0.1:60763 - "GET /api/buckets/ HTTP/1.1" 200 OK
2026-03-05 23:09:24,638 - app.main - WARNING - ⏱  GET /api/team/members  →  200  2373.4ms  🟡 SLOW
INFO:     127.0.0.1:60740 - "GET /api/team/members HTTP/1.1" 200 OK
2026-03-05 23:09:24,639 - app.main - WARNING - ⏱  GET /api/buckets/stats/activity  →  200  2374.1ms  🟡 SLOW
INFO:     127.0.0.1:60764 - "GET /api/buckets/stats/activity?days=30 HTTP/1.1" 200 OK
2026-03-05 23:09:24,836 - app.main - INFO - ⏱  GET /api/notifications/unread-count  →  200  198.8ms  🟢
INFO:     127.0.0.1:60751 - "GET /api/notifications/unread-count HTTP/1.1" 200 OK
2026-03-05 23:09:24,838 - app.routers.stripe - INFO - [Usage] Plan=premium
2026-03-05 23:09:24,839 - tracer - INFO - [06c9f65c] START GET /api/buckets/stats/dashboard  user_id=48c4c78c-bdfb-41b0-85d1-cadd60b9c555
2026-03-05 23:09:25,030 - tracer - INFO - [06c9f65c]   🟢 DB query bucket stats  190.1ms (total 190.1ms)  
2026-03-05 23:09:25,030 - tracer - INFO - [06c9f65c] END GET /api/buckets/stats/dashboard  OK 200  190.5ms  🟢  steps=1  slowest=DB query bucket stats(190.1ms)
2026-03-05 23:09:25,032 - app.main - INFO - ⏱  GET /dev/errors  →  200  196.2ms  🟢
INFO:     127.0.0.1:60761 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:09:25,034 - app.main - WARNING - ⏱  GET /api/stripe/usage  →  200  4371.5ms  🟡 SLOW
INFO:     127.0.0.1:60759 - "GET /api/stripe/usage HTTP/1.1" 200 OK
2026-03-05 23:09:25,034 - app.main - INFO - ⏱  GET /api/buckets/stats/dashboard  →  200  196.9ms  🟢
INFO:     127.0.0.1:60763 - "GET /api/buckets/stats/dashboard HTTP/1.1" 200 OK
2026-03-05 23:09:25,035 - tracer - INFO - [81036136] START GET /api/buckets  user_id=48c4c78c-bdfb-41b0-85d1-cadd60b9c555
2026-03-05 23:09:25,035 - tracer - INFO - [81036136]   🟢 get_effective_user_id  0.1ms (total 0.1ms)  
2026-03-05 23:09:25,035 - tracer - INFO - [81036136]   🟢 get_member_accessible_buckets  0.1ms (total 0.2ms)  
2026-03-05 23:09:25,236 - tracer - INFO - [81036136]   🟢 DB query buckets  200.8ms (total 201.0ms)  count=67
2026-03-05 23:09:25,237 - tracer - INFO - [81036136] END GET /api/buckets  OK 200  201.9ms  🟢  steps=3  slowest=DB query buckets(200.8ms)
2026-03-05 23:09:25,240 - tracer - INFO - [6ce14c35] START GET /api/buckets/stats/activity  user_id=48c4c78c-bdfb-41b0-85d1-cadd60b9c555
2026-03-05 23:09:25,613 - tracer - INFO - [6ce14c35]   🟢 DB query baselines  373.0ms (total 373.0ms)  
2026-03-05 23:09:25,981 - tracer - INFO - [6ce14c35]   🟢 DB query range data  368.3ms (total 741.3ms)  
2026-03-05 23:09:25,982 - tracer - INFO - [6ce14c35] END GET /api/buckets/stats/activity  OK 200  742.3ms  🟢  steps=2  slowest=DB query baselines(373.0ms)
2026-03-05 23:09:27,442 - app.main - WARNING - ⏱  GET /api/buckets/  →  200  2408.9ms  🟡 SLOW
INFO:     127.0.0.1:60764 - "GET /api/buckets/ HTTP/1.1" 200 OK
2026-03-05 23:09:27,442 - app.main - WARNING - ⏱  GET /api/buckets/stats/activity  →  200  2409.2ms  🟡 SLOW
INFO:     127.0.0.1:60740 - "GET /api/buckets/stats/activity?days=30 HTTP/1.1" 200 OK
2026-03-05 23:09:27,443 - app.main - WARNING - ⏱  GET /api/team/members  →  200  1459.8ms  🟡 SLOW
INFO:     127.0.0.1:60751 - "GET /api/team/members HTTP/1.1" 200 OK
INFO:     127.0.0.1:60761 - "OPTIONS /api/buckets/stats/activity?start_date=2026-02-26&end_date=2026-03-05 HTTP/1.1" 200 OK
2026-03-05 23:09:27,445 - app.routers.stripe - INFO - [Usage] Getting usage for user=48c4c78c-bdfb-41b0-85d1-cadd60b9c555
2026-03-05 23:09:27,445 - app.routers.stripe - INFO - [Usage] Plan=premium
INFO:     127.0.0.1:60759 - "OPTIONS /api/buckets/stats/activity?start_date=2026-02-26&end_date=2026-03-05 HTTP/1.1" 200 OK
2026-03-05 23:09:27,446 - app.main - INFO - ⏱  GET /api/stripe/usage  →  200  1.7ms  🟢
INFO:     127.0.0.1:60763 - "GET /api/stripe/usage HTTP/1.1" 200 OK
2026-03-05 23:09:27,447 - app.main - INFO - ⏱  GET /dev/errors  →  200  0.8ms  🟢
INFO:     127.0.0.1:60740 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:09:27,455 - tracer - INFO - [41edf768] START GET /api/buckets/stats/activity  user_id=48c4c78c-bdfb-41b0-85d1-cadd60b9c555
2026-03-05 23:09:27,821 - tracer - INFO - [41edf768]   🟢 DB query baselines  365.6ms (total 365.6ms)  
2026-03-05 23:09:28,176 - tracer - INFO - [41edf768]   🟢 DB query range data  355.7ms (total 721.3ms)  
2026-03-05 23:09:28,177 - tracer - INFO - [41edf768] END GET /api/buckets/stats/activity  OK 200  721.7ms  🟢  steps=2  slowest=DB query baselines(365.6ms)
2026-03-05 23:09:28,177 - app.main - INFO - ⏱  GET /api/buckets/stats/activity  →  200  723.1ms  🟢
INFO:     127.0.0.1:60740 - "GET /api/buckets/stats/activity?start_date=2026-02-26&end_date=2026-03-05 HTTP/1.1" 200 OK
2026-03-05 23:09:28,179 - tracer - INFO - [f80e5248] START GET /api/buckets/stats/activity  user_id=48c4c78c-bdfb-41b0-85d1-cadd60b9c555
2026-03-05 23:09:28,546 - tracer - INFO - [f80e5248]   🟢 DB query baselines  367.5ms (total 367.5ms)  
2026-03-05 23:09:28,911 - tracer - INFO - [f80e5248]   🟢 DB query range data  364.3ms (total 731.8ms)  
2026-03-05 23:09:28,911 - tracer - INFO - [f80e5248] END GET /api/buckets/stats/activity  OK 200  732.4ms  🟢  steps=2  slowest=DB query baselines(367.5ms)
2026-03-05 23:09:28,912 - app.main - INFO - ⏱  GET /api/buckets/stats/activity  →  200  733.7ms  🟢
INFO:     127.0.0.1:60763 - "GET /api/buckets/stats/activity?start_date=2026-02-26&end_date=2026-03-05 HTTP/1.1" 200 OK
2026-03-05 23:09:30,274 - app.main - INFO - ⏱  GET /dev/errors  →  200  0.8ms  🟢
INFO:     127.0.0.1:60763 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:09:34,277 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.1ms  🟢
INFO:     127.0.0.1:60763 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:09:38,284 - app.main - INFO - ⏱  GET /dev/errors  →  200  6.9ms  🟢
INFO:     127.0.0.1:60763 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:09:42,281 - app.main - INFO - ⏱  GET /dev/errors  →  200  0.9ms  🟢
INFO:     127.0.0.1:60763 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:09:46,281 - app.main - INFO - ⏱  GET /dev/errors  →  200  3.1ms  🟢
INFO:     127.0.0.1:60763 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:09:50,277 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.1ms  🟢
INFO:     127.0.0.1:60763 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:09:54,283 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.7ms  🟢
INFO:     127.0.0.1:60763 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:09:58,273 - app.main - INFO - ⏱  GET /dev/errors  →  200  0.9ms  🟢
INFO:     127.0.0.1:60763 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:10:02,276 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.2ms  🟢
INFO:     127.0.0.1:60763 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:10:06,276 - app.main - INFO - ⏱  GET /dev/errors  →  200  0.9ms  🟢
INFO:     127.0.0.1:60763 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:10:10,275 - app.main - INFO - ⏱  GET /dev/errors  →  200  0.6ms  🟢
INFO:     127.0.0.1:60763 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:10:14,277 - app.main - INFO - ⏱  GET /dev/errors  →  200  0.9ms  🟢
INFO:     127.0.0.1:60763 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:10:18,275 - app.main - INFO - ⏱  GET /dev/errors  →  200  0.9ms  🟢
INFO:     127.0.0.1:60763 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:10:20,285 - app.routers.stripe - INFO - [Usage] Getting usage for user=48c4c78c-bdfb-41b0-85d1-cadd60b9c555
2026-03-05 23:10:20,286 - app.routers.stripe - INFO - [Usage] Plan=premium
2026-03-05 23:10:20,287 - app.main - INFO - ⏱  GET /api/stripe/usage  →  200  6.5ms  🟢
INFO:     127.0.0.1:60763 - "GET /api/stripe/usage HTTP/1.1" 200 OK
2026-03-05 23:10:28,035 - app.main - INFO - ⏱  GET /dev/errors  →  200  0.9ms  🟢
INFO:     127.0.0.1:60917 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:10:29,811 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.0ms  🟢
INFO:     127.0.0.1:60917 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:10:33,813 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.2ms  🟢
INFO:     127.0.0.1:60917 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:10:37,813 - app.main - INFO - ⏱  GET /dev/errors  →  200  2.2ms  🟢
INFO:     127.0.0.1:60917 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:10:41,817 - app.main - INFO - ⏱  GET /dev/errors  →  200  0.6ms  🟢
INFO:     127.0.0.1:60917 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:10:45,813 - app.main - INFO - ⏱  GET /dev/errors  →  200  2.5ms  🟢
INFO:     127.0.0.1:60917 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:10:49,811 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.1ms  🟢
INFO:     127.0.0.1:60917 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:10:53,808 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.0ms  🟢
INFO:     127.0.0.1:60917 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:10:55,615 - tracer - INFO - [64bf7f60] START POST /api/buckets  user_id=48c4c78c-bdfb-41b0-85d1-cadd60b9c555 name=f
2026-03-05 23:10:55,924 - tracer - INFO - [64bf7f60]   🟢 Team member check  309.3ms (total 309.3ms)  
2026-03-05 23:10:56,140 - tracer - INFO - [64bf7f60]   🟢 Enforce bucket limit  215.9ms (total 525.2ms)  
2026-03-05 23:10:56,361 - tracer - INFO - [64bf7f60]   🟢 DB insert bucket  220.7ms (total 745.9ms)  
2026-03-05 23:10:56,361 - tracer - INFO - [64bf7f60] END POST /api/buckets  OK 200  746.1ms  🟢  steps=3  slowest=Team member check(309.3ms)
2026-03-05 23:10:56,366 - app.main - INFO - ⏱  POST /api/buckets/  →  200  763.0ms  🟢
INFO:     127.0.0.1:60917 - "POST /api/buckets/ HTTP/1.1" 200 OK
INFO:     127.0.0.1:60917 - "OPTIONS /api/buckets/e7e5c7df-7bcf-481d-8115-a97bf3ac8bc3 HTTP/1.1" 200 OK
INFO:     127.0.0.1:60930 - "OPTIONS /api/buckets/e7e5c7df-7bcf-481d-8115-a97bf3ac8bc3/files HTTP/1.1" 200 OK
INFO:     127.0.0.1:60933 - "OPTIONS /api/buckets/e7e5c7df-7bcf-481d-8115-a97bf3ac8bc3 HTTP/1.1" 200 OK
2026-03-05 23:10:56,410 - tracer - INFO - [e3cfd202] START GET /api/buckets/{id}  user_id=48c4c78c-bdfb-41b0-85d1-cadd60b9c555 bucket_id=e7e5c7df-7bcf-481d-8115-a97bf3ac8bc3
2026-03-05 23:10:56,410 - tracer - INFO - [e3cfd202]   🟢 get_effective_user_id  0.1ms (total 0.1ms)  
2026-03-05 23:10:56,410 - tracer - INFO - [e3cfd202]   🟢 check_bucket_permission  0.1ms (total 0.2ms)  
2026-03-05 23:10:56,594 - tracer - INFO - [e3cfd202]   🟢 DB query bucket  184.5ms (total 184.7ms)  
2026-03-05 23:10:56,595 - tracer - INFO - [e3cfd202] END GET /api/buckets/{id}  OK 200  185.0ms  🟢  steps=3  slowest=DB query bucket(184.5ms)
INFO:     127.0.0.1:60934 - "OPTIONS /api/buckets/e7e5c7df-7bcf-481d-8115-a97bf3ac8bc3/files HTTP/1.1" 200 OK
2026-03-05 23:10:56,597 - app.main - INFO - ⏱  GET /api/buckets/e7e5c7df-7bcf-481d-8115-a97bf3ac8bc3  →  200  190.4ms  🟢
INFO:     127.0.0.1:60937 - "GET /api/buckets/e7e5c7df-7bcf-481d-8115-a97bf3ac8bc3 HTTP/1.1" 200 OK
2026-03-05 23:10:56,607 - tracer - INFO - [a1534cea] START GET /api/buckets/{id}/files  user_id=48c4c78c-bdfb-41b0-85d1-cadd60b9c555 bucket_id=e7e5c7df-7bcf-481d-8115-a97bf3ac8bc3
2026-03-05 23:10:56,607 - tracer - INFO - [a1534cea]   🟢 get_effective_user_id  0.3ms (total 0.3ms)  
2026-03-05 23:10:56,802 - tracer - INFO - [a1534cea]   🟢 DB verify bucket  194.4ms (total 194.7ms)  
2026-03-05 23:10:57,006 - tracer - INFO - [a1534cea]   🟢 DB query files  203.9ms (total 398.6ms)  count=0
2026-03-05 23:10:57,006 - tracer - INFO - [a1534cea] END GET /api/buckets/{id}/files  OK 200  398.8ms  🟢  steps=3  slowest=DB query files(203.9ms)
2026-03-05 23:10:57,008 - app.main - INFO - ⏱  GET /api/buckets/e7e5c7df-7bcf-481d-8115-a97bf3ac8bc3/files  →  200  409.5ms  🟢
INFO:     127.0.0.1:60939 - "GET /api/buckets/e7e5c7df-7bcf-481d-8115-a97bf3ac8bc3/files HTTP/1.1" 200 OK
2026-03-05 23:10:57,010 - tracer - INFO - [bf9f440c] START GET /api/buckets/{id}  user_id=48c4c78c-bdfb-41b0-85d1-cadd60b9c555 bucket_id=e7e5c7df-7bcf-481d-8115-a97bf3ac8bc3
2026-03-05 23:10:57,010 - tracer - INFO - [bf9f440c]   🟢 get_effective_user_id  0.1ms (total 0.1ms)  
2026-03-05 23:10:57,010 - tracer - INFO - [bf9f440c]   🟢 check_bucket_permission  0.2ms (total 0.3ms)  
2026-03-05 23:10:57,196 - tracer - INFO - [bf9f440c]   🟢 DB query bucket  186.0ms (total 186.4ms)  
2026-03-05 23:10:57,197 - tracer - INFO - [bf9f440c] END GET /api/buckets/{id}  OK 200  186.7ms  🟢  steps=3  slowest=DB query bucket(186.0ms)
2026-03-05 23:10:57,199 - app.main - INFO - ⏱  GET /api/buckets/e7e5c7df-7bcf-481d-8115-a97bf3ac8bc3  →  200  190.4ms  🟢
INFO:     127.0.0.1:60941 - "GET /api/buckets/e7e5c7df-7bcf-481d-8115-a97bf3ac8bc3 HTTP/1.1" 200 OK
2026-03-05 23:10:57,201 - tracer - INFO - [5ac8af83] START GET /api/buckets/{id}/files  user_id=48c4c78c-bdfb-41b0-85d1-cadd60b9c555 bucket_id=e7e5c7df-7bcf-481d-8115-a97bf3ac8bc3
2026-03-05 23:10:57,201 - tracer - INFO - [5ac8af83]   🟢 get_effective_user_id  0.1ms (total 0.1ms)  
2026-03-05 23:10:57,384 - tracer - INFO - [5ac8af83]   🟢 DB verify bucket  182.9ms (total 183.0ms)  
2026-03-05 23:10:57,565 - tracer - INFO - [5ac8af83]   🟢 DB query files  180.7ms (total 363.7ms)  count=0
2026-03-05 23:10:57,565 - tracer - INFO - [5ac8af83] END GET /api/buckets/{id}/files  OK 200  363.7ms  🟢  steps=3  slowest=DB verify bucket(182.9ms)
2026-03-05 23:10:57,566 - app.main - INFO - ⏱  GET /api/buckets/e7e5c7df-7bcf-481d-8115-a97bf3ac8bc3/files  →  200  366.9ms  🟢
INFO:     127.0.0.1:60937 - "GET /api/buckets/e7e5c7df-7bcf-481d-8115-a97bf3ac8bc3/files HTTP/1.1" 200 OK
INFO:     127.0.0.1:60939 - "OPTIONS /api/buckets/e7e5c7df-7bcf-481d-8115-a97bf3ac8bc3/conversations HTTP/1.1" 200 OK
INFO:     127.0.0.1:60943 - "OPTIONS /api/buckets/e7e5c7df-7bcf-481d-8115-a97bf3ac8bc3/conversations HTTP/1.1" 200 OK
2026-03-05 23:10:57,570 - tracer - INFO - [8f1461ba] START GET /api/buckets/{id}/conversations  user_id=48c4c78c-bdfb-41b0-85d1-cadd60b9c555 bucket_id=e7e5c7df-7bcf-481d-8115-a97bf3ac8bc3
2026-03-05 23:10:57,570 - tracer - INFO - [8f1461ba]   🟢 get_effective_user_id  0.0ms (total 0.0ms)  
2026-03-05 23:10:57,755 - tracer - INFO - [8f1461ba]   🟢 DB verify bucket  185.2ms (total 185.2ms)  
2026-03-05 23:10:57,946 - tracer - INFO - [8f1461ba]   🟢 DB query conversations  190.6ms (total 375.8ms)  count=0
2026-03-05 23:10:57,946 - tracer - INFO - [8f1461ba] END GET /api/buckets/{id}/conversations  OK 200  376.0ms  🟢  steps=3  slowest=DB query conversations(190.6ms)
2026-03-05 23:10:57,946 - app.main - INFO - ⏱  GET /api/buckets/e7e5c7df-7bcf-481d-8115-a97bf3ac8bc3/conversations  →  200  379.0ms  🟢
INFO:     127.0.0.1:60937 - "GET /api/buckets/e7e5c7df-7bcf-481d-8115-a97bf3ac8bc3/conversations HTTP/1.1" 200 OK
2026-03-05 23:10:57,947 - app.main - INFO - ⏱  GET /dev/errors  →  200  0.6ms  🟢
INFO:     127.0.0.1:60943 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:10:57,948 - tracer - INFO - [4e5ae4ed] START GET /api/buckets/{id}/conversations  user_id=48c4c78c-bdfb-41b0-85d1-cadd60b9c555 bucket_id=e7e5c7df-7bcf-481d-8115-a97bf3ac8bc3
2026-03-05 23:10:57,948 - tracer - INFO - [4e5ae4ed]   🟢 get_effective_user_id  0.0ms (total 0.0ms)  
2026-03-05 23:10:58,132 - tracer - INFO - [4e5ae4ed]   🟢 DB verify bucket  184.1ms (total 184.1ms)  
2026-03-05 23:10:58,314 - tracer - INFO - [4e5ae4ed]   🟢 DB query conversations  181.9ms (total 366.1ms)  count=0
2026-03-05 23:10:58,314 - tracer - INFO - [4e5ae4ed] END GET /api/buckets/{id}/conversations  OK 200  366.5ms  🟢  steps=3  slowest=DB verify bucket(184.1ms)
2026-03-05 23:10:58,315 - app.main - INFO - ⏱  GET /api/buckets/e7e5c7df-7bcf-481d-8115-a97bf3ac8bc3/conversations  →  200  367.4ms  🟢
INFO:     127.0.0.1:60941 - "GET /api/buckets/e7e5c7df-7bcf-481d-8115-a97bf3ac8bc3/conversations HTTP/1.1" 200 OK
2026-03-05 23:11:01,811 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.1ms  🟢
INFO:     127.0.0.1:60941 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:11:05,810 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.0ms  🟢
INFO:     127.0.0.1:60941 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:11:09,810 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.4ms  🟢
INFO:     127.0.0.1:60941 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:11:13,811 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.0ms  🟢
INFO:     127.0.0.1:60941 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:11:17,810 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.1ms  🟢
INFO:     127.0.0.1:60941 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:11:21,810 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.0ms  🟢
INFO:     127.0.0.1:60941 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:11:25,811 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.0ms  🟢
INFO:     127.0.0.1:60941 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:11:29,810 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.1ms  🟢
INFO:     127.0.0.1:60941 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:11:33,811 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.5ms  🟢
INFO:     127.0.0.1:60941 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:11:37,811 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.1ms  🟢
INFO:     127.0.0.1:60941 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:11:41,808 - app.main - INFO - ⏱  GET /dev/errors  →  200  0.9ms  🟢
INFO:     127.0.0.1:60941 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
INFO:     127.0.0.1:60941 - "OPTIONS /api/buckets/e7e5c7df-7bcf-481d-8115-a97bf3ac8bc3/upload HTTP/1.1" 200 OK
2026-03-05 23:11:45,015 - tracer - INFO - [5ec42a49] START POST /api/buckets/{id}/upload  user_id=48c4c78c-bdfb-41b0-85d1-cadd60b9c555 bucket_id=e7e5c7df-7bcf-481d-8115-a97bf3ac8bc3 filename=norseorganic page.pdf
2026-03-05 23:11:45,634 - tracer - INFO - [5ec42a49]   🟢 Team service checks  619.0ms (total 619.0ms)  
2026-03-05 23:11:45,832 - tracer - INFO - [5ec42a49]   🟢 DB verify bucket  198.3ms (total 817.2ms)  
2026-03-05 23:11:45,834 - app.main - INFO - ⏱  GET /dev/errors  →  200  0.8ms  🟢
INFO:     127.0.0.1:60956 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:11:45,856 - tracer - INFO - [5ec42a49]   🟢 Read file content  24.0ms (total 841.2ms)  size=42510291
2026-03-05 23:11:46,420 - tracer - INFO - [5ec42a49]   🟢 Check plan limits  564.3ms (total 1405.5ms)  
2026-03-05 23:11:52,283 - tracer - INFO - [5ec42a49]   🔴 Upload to Supabase Storage  5862.2ms (total 7267.7ms)  
2026-03-05 23:11:52,550 - tracer - INFO - [5ec42a49]   🟢 DB insert file record  267.6ms (total 7535.3ms)  
2026-03-05 23:11:52,807 - app.services.notifications - INFO - ✅ Notification created for user 48c4c78c-bdfb-41b0-85d1-cadd60b9c555: File Uploaded
2026-03-05 23:11:52,807 - tracer - INFO - [5ec42a49] END POST /api/buckets/{id}/upload  OK 200  7792.6ms  🔴  steps=6  slowest=Upload to Supabase Storage(5862.2ms)
2026-03-05 23:11:52,808 - tracer - WARNING - [5ec42a49] SLOW TRACE: Team service checks(619.0ms) -> DB verify bucket(198.3ms) -> Read file content(24.0ms) -> Check plan limits(564.3ms) -> Upload to Supabase Storage(5862.2ms) -> DB insert file record(267.6ms)
2026-03-05 23:11:52,810 - app.main - ERROR - ⏱  POST /api/buckets/e7e5c7df-7bcf-481d-8115-a97bf3ac8bc3/upload  →  200  7885.4ms  🔴 VERY SLOW
INFO:     127.0.0.1:60941 - "POST /api/buckets/e7e5c7df-7bcf-481d-8115-a97bf3ac8bc3/upload HTTP/1.1" 200 OK
2026-03-05 23:11:52,812 - app.main - INFO - ⏱  GET /dev/errors  →  200  2.8ms  🟢
INFO:     127.0.0.1:60956 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:11:52,817 - app.routers.files - INFO - ================================================================================
2026-03-05 23:11:52,817 - app.routers.files - INFO - 🔄 BACKGROUND PROCESSING STARTED: norseorganic page.pdf
2026-03-05 23:11:52,817 - app.routers.files - INFO -    File ID: c124ede1-ae3c-40df-8816-13a7ef6214a9
2026-03-05 23:11:52,817 - app.routers.files - INFO -    Storage Path: 48c4c78c-bdfb-41b0-85d1-cadd60b9c555/e7e5c7df-7bcf-481d-8115-a97bf3ac8bc3/b40da71c-c0b1-483e-9fac-f92b6a8525e8.pdf
2026-03-05 23:11:52,818 - app.routers.files - INFO -    MIME Type: application/pdf
2026-03-05 23:11:52,827 - tracer - INFO - [17f8d699] START GET /api/buckets/{id}  user_id=48c4c78c-bdfb-41b0-85d1-cadd60b9c555 bucket_id=e7e5c7df-7bcf-481d-8115-a97bf3ac8bc3
2026-03-05 23:11:52,827 - tracer - INFO - [17f8d699]   🟢 get_effective_user_id  0.3ms (total 0.3ms)  
2026-03-05 23:11:52,827 - tracer - INFO - [17f8d699]   🟢 check_bucket_permission  0.1ms (total 0.4ms)  
2026-03-05 23:11:53,215 - tracer - INFO - [17f8d699]   🟢 DB query bucket  388.1ms (total 388.4ms)  
2026-03-05 23:11:53,216 - tracer - INFO - [17f8d699] END GET /api/buckets/{id}  OK 200  389.6ms  🟢  steps=3  slowest=DB query bucket(388.1ms)
2026-03-05 23:11:53,219 - app.routers.files - INFO - 📈 Progress stage transition: file_id=c124ede1-ae3c-40df-8816-13a7ef6214a9 stage=queued percent=0.00
2026-03-05 23:11:53,219 - tracer - INFO - [ed5cd4f4] START GET /api/buckets/{id}/files  user_id=48c4c78c-bdfb-41b0-85d1-cadd60b9c555 bucket_id=e7e5c7df-7bcf-481d-8115-a97bf3ac8bc3
2026-03-05 23:11:53,222 - tracer - INFO - [ed5cd4f4]   🟢 get_effective_user_id  2.5ms (total 2.5ms)  
2026-03-05 23:11:53,405 - tracer - INFO - [ed5cd4f4]   🟢 DB verify bucket  183.3ms (total 185.8ms)  
2026-03-05 23:11:53,409 - app.routers.files - INFO - 📈 Progress stage completed: file_id=c124ede1-ae3c-40df-8816-13a7ef6214a9 stage=queued duration=0.19s
2026-03-05 23:11:53,409 - app.routers.files - INFO - 📈 Progress stage transition: file_id=c124ede1-ae3c-40df-8816-13a7ef6214a9 stage=downloading percent=0.00
2026-03-05 23:11:53,602 - tracer - INFO - [ed5cd4f4]   🟢 DB query files  196.4ms (total 382.2ms)  count=1
2026-03-05 23:11:53,602 - tracer - INFO - [ed5cd4f4] END GET /api/buckets/{id}/files  OK 200  382.6ms  🟢  steps=3  slowest=DB query files(196.4ms)
2026-03-05 23:11:53,604 - app.routers.files - INFO -   1️⃣  Downloading file from storage...
2026-03-05 23:11:53,607 - app.main - INFO - ⏱  GET /api/buckets/e7e5c7df-7bcf-481d-8115-a97bf3ac8bc3  →  200  784.6ms  🟢
INFO:     127.0.0.1:60956 - "GET /api/buckets/e7e5c7df-7bcf-481d-8115-a97bf3ac8bc3 HTTP/1.1" 200 OK
2026-03-05 23:11:53,608 - app.main - INFO - ⏱  GET /api/buckets/e7e5c7df-7bcf-481d-8115-a97bf3ac8bc3/files  →  200  785.1ms  🟢
INFO:     127.0.0.1:60941 - "GET /api/buckets/e7e5c7df-7bcf-481d-8115-a97bf3ac8bc3/files HTTP/1.1" 200 OK
INFO:     127.0.0.1:60961 - "OPTIONS /api/buckets/e7e5c7df-7bcf-481d-8115-a97bf3ac8bc3/chat HTTP/1.1" 200 OK
2026-03-05 23:11:53,633 - tracer - INFO - [d28418e0] START POST /api/buckets/{id}/chat  user_id=48c4c78c-bdfb-41b0-85d1-cadd60b9c555 bucket_id=e7e5c7df-7bcf-481d-8115-a97bf3ac8bc3
2026-03-05 23:11:53,633 - tracer - INFO - [d28418e0]   🟢 Team service checks  0.1ms (total 0.1ms)  
2026-03-05 23:11:53,834 - app.services.plan_limits - WARNING - [get_metric_count] chat_messages/daily: 'NoneType' object has no attribute 'data'
2026-03-05 23:11:54,017 - app.services.plan_limits - WARNING - [get_metric_count] bucket_chat/hourly: 'NoneType' object has no attribute 'data'
2026-03-05 23:11:54,205 - app.services.plan_limits - WARNING - [get_metric_count] bucket_chat/daily: 'NoneType' object has no attribute 'data'
2026-03-05 23:11:54,205 - tracer - INFO - [d28418e0]   🟢 Enforce chat limits  572.0ms (total 572.1ms)  
2026-03-05 23:11:54,392 - tracer - INFO - [d28418e0]   🟢 DB verify bucket  186.7ms (total 758.8ms)  
2026-03-05 23:11:54,404 - app.main - INFO - ⏱  GET /dev/errors  →  200  10.9ms  🟢
INFO:     127.0.0.1:60956 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:11:54,625 - tracer - INFO - [d28418e0]   🟢 Parallel fetch: files+chunks+summaries  233.7ms (total 992.4ms)  files=1 chunks=0 summaries=0
2026-03-05 23:11:54,626 - tracer - INFO - [d28418e0]   🟢 Context built  0.4ms (total 992.9ms)  context_len=202
2026-03-05 23:11:54,626 - tracer - INFO - [d28418e0]   🟢 Web search check  0.2ms (total 993.1ms)  triggered=False
2026-03-05 23:11:54,816 - tracer - INFO - [d28418e0]   🟢 Created new conversation  189.6ms (total 1182.7ms)  
2026-03-05 23:11:55,019 - tracer - INFO - [d28418e0]   🟢 Fetch conversation history  203.8ms (total 1386.5ms)  messages=0
2026-03-05 23:11:55,219 - tracer - INFO - [d28418e0]   🟢 Saved user message  199.4ms (total 1585.9ms)  
2026-03-05 23:11:55,219 - tracer - INFO - [d28418e0]   🟢 Processing guard armed  0.3ms (total 1586.2ms)  pending=1
2026-03-05 23:11:55,219 - app.routers.chat - INFO - [CHAT_GUARD] WAIT bucket=e7e5c7df-7bcf-481d-8115-a97bf3ac8bc3 pending=1 mentions_attachment=False has_indexed_content=False
2026-03-05 23:11:55,219 - tracer - INFO - [d28418e0]   🟢 Sources + messages prepared  0.3ms (total 1586.5ms)  sources=0 ai_msgs=3
2026-03-05 23:11:55,219 - tracer - INFO - [d28418e0] END POST /api/buckets/{id}/chat  OK 200  1586.5ms  🟡  steps=11  slowest=Enforce chat limits(572.0ms)
2026-03-05 23:11:55,220 - tracer - INFO - [8a6a3f73] START STREAM chat  bucket_id=e7e5c7df-7bcf-481d-8115-a97bf3ac8bc3
2026-03-05 23:11:55,221 - app.routers.chat - INFO - [STREAM] ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
2026-03-05 23:11:55,221 - app.routers.chat - INFO - [STREAM] START  bucket=e7e5c7df-7bcf-481d-8115-a97bf3ac8bc3  msg_len=113  files=1  chunks_loaded=0  summaries=0  context_len=202  web_search=False
2026-03-05 23:11:55,221 - app.routers.chat - INFO - [STREAM] AI messages count: 3, total context chars sent to AI: 3223
2026-03-05 23:11:55,221 - app.main - WARNING - ⏱  POST /api/buckets/e7e5c7df-7bcf-481d-8115-a97bf3ac8bc3/chat  →  200  1608.9ms  🟡 SLOW
INFO:     127.0.0.1:60961 - "POST /api/buckets/e7e5c7df-7bcf-481d-8115-a97bf3ac8bc3/chat HTTP/1.1" 200 OK
2026-03-05 23:11:57,810 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.0ms  🟢
INFO:     127.0.0.1:60956 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:11:58,147 - app.routers.files - INFO -   ✅ Downloaded (42510291 bytes)
2026-03-05 23:11:58,333 - app.routers.files - INFO -   2️⃣  Extracting text from norseorganic page.pdf...
2026-03-05 23:11:58,334 - app.routers.files - INFO - 📈 Progress stage completed: file_id=c124ede1-ae3c-40df-8816-13a7ef6214a9 stage=downloading duration=4.92s
2026-03-05 23:11:58,334 - app.routers.files - INFO - 📈 Progress stage transition: file_id=c124ede1-ae3c-40df-8816-13a7ef6214a9 stage=extracting percent=10.00
2026-03-05 23:11:58,521 - app.services.file_processor - INFO - 📄 Processing PDF with PyMuPDF: /Volumes/KIOXIA/AIveilix/.tmp/tmp7ar75k45.pdf
2026-03-05 23:11:58,602 - app.services.file_processor - INFO -   🖼️  Found 62 images on page 1
2026-03-05 23:12:01,106 - app.services.file_processor - INFO -   📊 Extracted 62 images from 1 pages - processing in batches of 50 with up to 5 workers
2026-03-05 23:12:01,106 - app.routers.files - INFO - 📈 Progress stage completed: file_id=c124ede1-ae3c-40df-8816-13a7ef6214a9 stage=extracting duration=2.77s
2026-03-05 23:12:01,106 - app.routers.files - INFO - 📈 Progress stage transition: file_id=c124ede1-ae3c-40df-8816-13a7ef6214a9 stage=image_ocr percent=25.00
2026-03-05 23:12:01,284 - app.services.file_processor - INFO -   🚚 Processing image batch 1/2 (50 images, workers=5)
2026-03-05 23:12:01,285 - app.services.file_processor - INFO - 🖼️  Processing image with gemini-2.5-flash: PDF_Page1_Image1
2026-03-05 23:12:01,286 - app.services.file_processor - INFO - 🖼️  Processing image with gemini-2.5-flash: PDF_Page1_Image2
2026-03-05 23:12:01,287 - app.services.file_processor - INFO - 🖼️  Processing image with gemini-2.5-flash: PDF_Page1_Image3
2026-03-05 23:12:01,287 - app.services.file_processor - INFO - 🖼️  Processing image with gemini-2.5-flash: PDF_Page1_Image4
2026-03-05 23:12:01,288 - app.services.file_processor - INFO - 🖼️  Processing image with gemini-2.5-flash: PDF_Page1_Image5
2026-03-05 23:12:01,358 - app.services.file_processor - INFO -   🤖 Calling Gemini Vision API (gemini-2.5-flash) for PDF_Page1_Image2...
2026-03-05 23:12:01,358 - app.services.file_processor - INFO -   🤖 Calling Gemini Vision API (gemini-2.5-flash) for PDF_Page1_Image1...
2026-03-05 23:12:01,358 - app.services.file_processor - INFO -   🤖 Calling Gemini Vision API (gemini-2.5-flash) for PDF_Page1_Image4...
2026-03-05 23:12:01,358 - app.services.file_processor - INFO -   🤖 Calling Gemini Vision API (gemini-2.5-flash) for PDF_Page1_Image3...
2026-03-05 23:12:01,358 - app.services.file_processor - INFO -   🤖 Calling Gemini Vision API (gemini-2.5-flash) for PDF_Page1_Image5...
2026-03-05 23:12:01,811 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.5ms  🟢
INFO:     127.0.0.1:60956 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:12:05,811 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.1ms  🟢
INFO:     127.0.0.1:60956 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:12:09,810 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.5ms  🟢
INFO:     127.0.0.1:60956 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:12:10,517 - app.services.file_processor - INFO -   ✅ Gemini Vision analysis complete for PDF_Page1_Image5
2026-03-05 23:12:10,518 - app.services.file_processor - INFO - 🖼️  Processing image with gemini-2.5-flash: PDF_Page1_Image6
2026-03-05 23:12:10,519 - app.services.file_processor - INFO -   🤖 Calling Gemini Vision API (gemini-2.5-flash) for PDF_Page1_Image6...
2026-03-05 23:12:10,519 - app.services.file_processor - INFO -     ✅ Image 5 on page 1 done (1/62)
2026-03-05 23:12:13,810 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.0ms  🟢
INFO:     127.0.0.1:60956 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:12:17,810 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.1ms  🟢
INFO:     127.0.0.1:60956 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:12:20,910 - app.services.file_processor - INFO -   ✅ Gemini Vision analysis complete for PDF_Page1_Image4
2026-03-05 23:12:20,911 - app.services.file_processor - INFO - 🖼️  Processing image with gemini-2.5-flash: PDF_Page1_Image7
2026-03-05 23:12:20,912 - app.services.file_processor - INFO -     ✅ Image 4 on page 1 done (2/62)
2026-03-05 23:12:20,915 - app.services.file_processor - INFO -   🤖 Calling Gemini Vision API (gemini-2.5-flash) for PDF_Page1_Image7...
2026-03-05 23:12:21,808 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.1ms  🟢
INFO:     127.0.0.1:60956 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:12:22,045 - app.services.file_processor - INFO -   ✅ Gemini Vision analysis complete for PDF_Page1_Image2
2026-03-05 23:12:22,046 - app.services.file_processor - INFO - 🖼️  Processing image with gemini-2.5-flash: PDF_Page1_Image8
2026-03-05 23:12:22,046 - app.services.file_processor - INFO -     ✅ Image 2 on page 1 done (3/62)
2026-03-05 23:12:22,049 - app.services.file_processor - INFO -   🤖 Calling Gemini Vision API (gemini-2.5-flash) for PDF_Page1_Image8...
2026-03-05 23:12:23,106 - app.services.file_processor - INFO -   ✅ Gemini Vision analysis complete for PDF_Page1_Image3
2026-03-05 23:12:23,107 - app.services.file_processor - INFO - 🖼️  Processing image with gemini-2.5-flash: PDF_Page1_Image9
2026-03-05 23:12:23,108 - app.services.file_processor - INFO -     ✅ Image 3 on page 1 done (4/62)
2026-03-05 23:12:23,111 - app.services.file_processor - INFO -   🤖 Calling Gemini Vision API (gemini-2.5-flash) for PDF_Page1_Image9...
2026-03-05 23:12:23,482 - app.services.file_processor - INFO -   ✅ Gemini Vision analysis complete for PDF_Page1_Image1
2026-03-05 23:12:23,483 - app.services.file_processor - INFO - 🖼️  Processing image with gemini-2.5-flash: PDF_Page1_Image10
2026-03-05 23:12:23,483 - app.services.file_processor - INFO -     ✅ Image 1 on page 1 done (5/62)
2026-03-05 23:12:23,484 - app.services.file_processor - INFO -   🤖 Calling Gemini Vision API (gemini-2.5-flash) for PDF_Page1_Image10...
2026-03-05 23:12:25,808 - app.main - INFO - ⏱  GET /dev/errors  →  200  0.2ms  🟢
INFO:     127.0.0.1:60956 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:12:29,808 - app.main - INFO - ⏱  GET /dev/errors  →  200  0.5ms  🟢
INFO:     127.0.0.1:60956 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:12:32,767 - app.services.file_processor - INFO -   ✅ Gemini Vision analysis complete for PDF_Page1_Image6
2026-03-05 23:12:32,768 - app.services.file_processor - INFO - 🖼️  Processing image with gemini-2.5-flash: PDF_Page1_Image11
2026-03-05 23:12:32,769 - app.services.file_processor - INFO -     ✅ Image 6 on page 1 done (6/62)
2026-03-05 23:12:32,769 - app.services.file_processor - INFO -   🤖 Calling Gemini Vision API (gemini-2.5-flash) for PDF_Page1_Image11...
2026-03-05 23:12:33,810 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.1ms  🟢
INFO:     127.0.0.1:60956 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:12:37,811 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.2ms  🟢
INFO:     127.0.0.1:60956 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:12:41,126 - app.services.file_processor - INFO -   ✅ Gemini Vision analysis complete for PDF_Page1_Image9
2026-03-05 23:12:41,126 - app.services.file_processor - INFO - 🖼️  Processing image with gemini-2.5-flash: PDF_Page1_Image12
2026-03-05 23:12:41,127 - app.services.file_processor - INFO -     ✅ Image 9 on page 1 done (7/62)
2026-03-05 23:12:41,130 - app.services.file_processor - INFO -   🤖 Calling Gemini Vision API (gemini-2.5-flash) for PDF_Page1_Image12...
2026-03-05 23:12:41,811 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.1ms  🟢
INFO:     127.0.0.1:60956 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:12:42,814 - app.services.file_processor - INFO -   ✅ Gemini Vision analysis complete for PDF_Page1_Image10
2026-03-05 23:12:42,814 - app.services.file_processor - INFO - 🖼️  Processing image with gemini-2.5-flash: PDF_Page1_Image13
2026-03-05 23:12:42,815 - app.services.file_processor - INFO -     ✅ Image 10 on page 1 done (8/62)
2026-03-05 23:12:42,815 - app.services.file_processor - INFO -   🤖 Calling Gemini Vision API (gemini-2.5-flash) for PDF_Page1_Image13...
2026-03-05 23:12:43,480 - app.services.file_processor - INFO -   ✅ Gemini Vision analysis complete for PDF_Page1_Image7
2026-03-05 23:12:43,481 - app.services.file_processor - INFO - 🖼️  Processing image with gemini-2.5-flash: PDF_Page1_Image14
2026-03-05 23:12:43,482 - app.services.file_processor - INFO -     ✅ Image 7 on page 1 done (9/62)
2026-03-05 23:12:43,482 - app.services.file_processor - INFO -   🤖 Calling Gemini Vision API (gemini-2.5-flash) for PDF_Page1_Image14...
2026-03-05 23:12:44,109 - app.services.file_processor - INFO -   ✅ Gemini Vision analysis complete for PDF_Page1_Image8
2026-03-05 23:12:44,109 - app.services.file_processor - INFO - 🖼️  Processing image with gemini-2.5-flash: PDF_Page1_Image15
2026-03-05 23:12:44,110 - app.services.file_processor - INFO -     ✅ Image 8 on page 1 done (10/62)
2026-03-05 23:12:44,113 - app.services.file_processor - INFO -   🤖 Calling Gemini Vision API (gemini-2.5-flash) for PDF_Page1_Image15...
2026-03-05 23:12:45,810 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.6ms  🟢
INFO:     127.0.0.1:60956 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:12:49,810 - app.main - INFO - ⏱  GET /dev/errors  →  200  0.5ms  🟢
INFO:     127.0.0.1:60956 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:12:50,144 - app.services.file_processor - INFO -   ✅ Gemini Vision analysis complete for PDF_Page1_Image13
2026-03-05 23:12:50,145 - app.services.file_processor - INFO - 🖼️  Processing image with gemini-2.5-flash: PDF_Page1_Image16
2026-03-05 23:12:50,146 - app.services.file_processor - INFO -     ✅ Image 13 on page 1 done (11/62)
2026-03-05 23:12:50,148 - app.services.file_processor - INFO -   🤖 Calling Gemini Vision API (gemini-2.5-flash) for PDF_Page1_Image16...
2026-03-05 23:12:51,885 - app.services.file_processor - INFO -   ✅ Gemini Vision analysis complete for PDF_Page1_Image11
2026-03-05 23:12:51,886 - app.services.file_processor - INFO - 🖼️  Processing image with gemini-2.5-flash: PDF_Page1_Image17
2026-03-05 23:12:51,887 - app.services.file_processor - INFO -     ✅ Image 11 on page 1 done (12/62)
2026-03-05 23:12:51,889 - app.services.file_processor - INFO -   🤖 Calling Gemini Vision API (gemini-2.5-flash) for PDF_Page1_Image17...
2026-03-05 23:12:53,808 - app.main - INFO - ⏱  GET /dev/errors  →  200  0.4ms  🟢
INFO:     127.0.0.1:60956 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:12:55,165 - app.services.file_processor - INFO -   ✅ Gemini Vision analysis complete for PDF_Page1_Image14
2026-03-05 23:12:55,165 - app.services.file_processor - INFO - 🖼️  Processing image with gemini-2.5-flash: PDF_Page1_Image18
2026-03-05 23:12:55,166 - app.services.file_processor - INFO -     ✅ Image 14 on page 1 done (13/62)
2026-03-05 23:12:55,167 - app.services.file_processor - INFO -   🤖 Calling Gemini Vision API (gemini-2.5-flash) for PDF_Page1_Image18...
2026-03-05 23:12:57,809 - app.main - INFO - ⏱  GET /dev/errors  →  200  0.6ms  🟢
INFO:     127.0.0.1:60956 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:12:59,324 - app.services.file_processor - INFO -   ✅ Gemini Vision analysis complete for PDF_Page1_Image12
2026-03-05 23:12:59,325 - app.services.file_processor - INFO - 🖼️  Processing image with gemini-2.5-flash: PDF_Page1_Image19
2026-03-05 23:12:59,326 - app.services.file_processor - INFO -     ✅ Image 12 on page 1 done (14/62)
2026-03-05 23:12:59,328 - app.services.file_processor - INFO -   🤖 Calling Gemini Vision API (gemini-2.5-flash) for PDF_Page1_Image19...
2026-03-05 23:13:01,810 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.0ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:13:02,899 - app.services.file_processor - INFO -   ✅ Gemini Vision analysis complete for PDF_Page1_Image15
2026-03-05 23:13:02,899 - app.services.file_processor - INFO - 🖼️  Processing image with gemini-2.5-flash: PDF_Page1_Image20
2026-03-05 23:13:02,900 - app.services.file_processor - INFO -     ✅ Image 15 on page 1 done (15/62)
2026-03-05 23:13:02,901 - app.services.file_processor - INFO -   🤖 Calling Gemini Vision API (gemini-2.5-flash) for PDF_Page1_Image20...
2026-03-05 23:13:05,810 - app.main - INFO - ⏱  GET /dev/errors  →  200  0.6ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:13:06,678 - app.services.file_processor - INFO -   ✅ Gemini Vision analysis complete for PDF_Page1_Image19
2026-03-05 23:13:06,679 - app.services.file_processor - INFO - 🖼️  Processing image with gemini-2.5-flash: PDF_Page1_Image21
2026-03-05 23:13:06,679 - app.services.file_processor - INFO -     ✅ Image 19 on page 1 done (16/62)
2026-03-05 23:13:06,681 - app.services.file_processor - INFO -   🤖 Calling Gemini Vision API (gemini-2.5-flash) for PDF_Page1_Image21...
2026-03-05 23:13:09,807 - app.main - INFO - ⏱  GET /dev/errors  →  200  0.3ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:13:12,872 - app.services.file_processor - INFO -   ✅ Gemini Vision analysis complete for PDF_Page1_Image18
2026-03-05 23:13:12,873 - app.services.file_processor - INFO - 🖼️  Processing image with gemini-2.5-flash: PDF_Page1_Image22
2026-03-05 23:13:12,874 - app.services.file_processor - INFO -     ✅ Image 18 on page 1 done (17/62)
2026-03-05 23:13:12,877 - app.services.file_processor - INFO -   🤖 Calling Gemini Vision API (gemini-2.5-flash) for PDF_Page1_Image22...
2026-03-05 23:13:13,668 - app.services.file_processor - INFO -   ✅ Gemini Vision analysis complete for PDF_Page1_Image16
2026-03-05 23:13:13,669 - app.services.file_processor - INFO - 🖼️  Processing image with gemini-2.5-flash: PDF_Page1_Image23
2026-03-05 23:13:13,670 - app.services.file_processor - INFO -   🤖 Calling Gemini Vision API (gemini-2.5-flash) for PDF_Page1_Image23...
2026-03-05 23:13:13,670 - app.services.file_processor - INFO -     ✅ Image 16 on page 1 done (18/62)
2026-03-05 23:13:13,810 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.1ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:13:14,519 - app.services.file_processor - INFO -   ✅ Gemini Vision analysis complete for PDF_Page1_Image17
2026-03-05 23:13:14,520 - app.services.file_processor - INFO - 🖼️  Processing image with gemini-2.5-flash: PDF_Page1_Image24
2026-03-05 23:13:14,521 - app.services.file_processor - INFO -     ✅ Image 17 on page 1 done (19/62)
2026-03-05 23:13:14,524 - app.services.file_processor - INFO -   🤖 Calling Gemini Vision API (gemini-2.5-flash) for PDF_Page1_Image24...
2026-03-05 23:13:17,813 - app.main - INFO - ⏱  GET /dev/errors  →  200  3.6ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:13:20,920 - app.services.file_processor - INFO -   ✅ Gemini Vision analysis complete for PDF_Page1_Image24
2026-03-05 23:13:20,921 - app.services.file_processor - INFO - 🖼️  Processing image with gemini-2.5-flash: PDF_Page1_Image25
2026-03-05 23:13:20,921 - app.services.file_processor - INFO -     ✅ Image 24 on page 1 done (20/62)
2026-03-05 23:13:20,924 - app.services.file_processor - INFO -   🤖 Calling Gemini Vision API (gemini-2.5-flash) for PDF_Page1_Image25...
2026-03-05 23:13:21,809 - app.main - INFO - ⏱  GET /dev/errors  →  200  0.9ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:13:23,237 - app.services.file_processor - INFO -   ✅ Gemini Vision analysis complete for PDF_Page1_Image21
2026-03-05 23:13:23,237 - app.services.file_processor - INFO - 🖼️  Processing image with gemini-2.5-flash: PDF_Page1_Image26
2026-03-05 23:13:23,238 - app.services.file_processor - INFO -     ✅ Image 21 on page 1 done (21/62)
2026-03-05 23:13:23,241 - app.services.file_processor - INFO -   🤖 Calling Gemini Vision API (gemini-2.5-flash) for PDF_Page1_Image26...
2026-03-05 23:13:25,309 - app.services.file_processor - INFO -   ✅ Gemini Vision analysis complete for PDF_Page1_Image20
2026-03-05 23:13:25,310 - app.services.file_processor - INFO - 🖼️  Processing image with gemini-2.5-flash: PDF_Page1_Image27
2026-03-05 23:13:25,311 - app.services.file_processor - INFO -   🤖 Calling Gemini Vision API (gemini-2.5-flash) for PDF_Page1_Image27...
2026-03-05 23:13:25,313 - app.services.file_processor - INFO -     ✅ Image 20 on page 1 done (22/62)
2026-03-05 23:13:25,809 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.3ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:13:28,853 - app.services.file_processor - INFO -   ✅ Gemini Vision analysis complete for PDF_Page1_Image22
2026-03-05 23:13:28,853 - app.services.file_processor - INFO - 🖼️  Processing image with gemini-2.5-flash: PDF_Page1_Image28
2026-03-05 23:13:28,854 - app.services.file_processor - INFO -     ✅ Image 22 on page 1 done (23/62)
2026-03-05 23:13:28,855 - app.services.file_processor - INFO -   🤖 Calling Gemini Vision API (gemini-2.5-flash) for PDF_Page1_Image28...
2026-03-05 23:13:29,811 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.2ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:13:31,283 - app.services.file_processor - INFO -   ✅ Gemini Vision analysis complete for PDF_Page1_Image23
2026-03-05 23:13:31,284 - app.services.file_processor - INFO - 🖼️  Processing image with gemini-2.5-flash: PDF_Page1_Image29
2026-03-05 23:13:31,285 - app.services.file_processor - INFO -     ✅ Image 23 on page 1 done (24/62)
2026-03-05 23:13:31,286 - app.services.file_processor - INFO -   🤖 Calling Gemini Vision API (gemini-2.5-flash) for PDF_Page1_Image29...
2026-03-05 23:13:33,809 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.0ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:13:34,794 - app.services.file_processor - INFO -   ✅ Gemini Vision analysis complete for PDF_Page1_Image25
2026-03-05 23:13:34,795 - app.services.file_processor - INFO - 🖼️  Processing image with gemini-2.5-flash: PDF_Page1_Image30
2026-03-05 23:13:34,796 - app.services.file_processor - INFO -     ✅ Image 25 on page 1 done (25/62)
2026-03-05 23:13:34,799 - app.services.file_processor - INFO -   🤖 Calling Gemini Vision API (gemini-2.5-flash) for PDF_Page1_Image30...
2026-03-05 23:13:37,810 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.1ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:13:38,681 - app.services.file_processor - INFO -   ✅ Gemini Vision analysis complete for PDF_Page1_Image28
2026-03-05 23:13:38,682 - app.services.file_processor - INFO - 🖼️  Processing image with gemini-2.5-flash: PDF_Page1_Image31
2026-03-05 23:13:38,682 - app.services.file_processor - INFO -     ✅ Image 28 on page 1 done (26/62)
2026-03-05 23:13:38,685 - app.services.file_processor - INFO -   🤖 Calling Gemini Vision API (gemini-2.5-flash) for PDF_Page1_Image31...
2026-03-05 23:13:39,604 - app.services.file_processor - INFO -   ✅ Gemini Vision analysis complete for PDF_Page1_Image26
2026-03-05 23:13:39,604 - app.services.file_processor - INFO - 🖼️  Processing image with gemini-2.5-flash: PDF_Page1_Image32
2026-03-05 23:13:39,605 - app.services.file_processor - INFO -     ✅ Image 26 on page 1 done (27/62)
2026-03-05 23:13:39,606 - app.services.file_processor - INFO -   🤖 Calling Gemini Vision API (gemini-2.5-flash) for PDF_Page1_Image32...
2026-03-05 23:13:39,665 - app.services.file_processor - INFO -   ✅ Gemini Vision analysis complete for PDF_Page1_Image27
2026-03-05 23:13:39,665 - app.services.file_processor - INFO - 🖼️  Processing image with gemini-2.5-flash: PDF_Page1_Image33
2026-03-05 23:13:39,666 - app.services.file_processor - INFO -     ✅ Image 27 on page 1 done (28/62)
2026-03-05 23:13:39,668 - app.services.file_processor - INFO -   🤖 Calling Gemini Vision API (gemini-2.5-flash) for PDF_Page1_Image33...
2026-03-05 23:13:41,809 - app.main - INFO - ⏱  GET /dev/errors  →  200  0.8ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:13:45,811 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.1ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:13:49,290 - app.services.file_processor - INFO -   ✅ Gemini Vision analysis complete for PDF_Page1_Image29
2026-03-05 23:13:49,291 - app.services.file_processor - INFO - 🖼️  Processing image with gemini-2.5-flash: PDF_Page1_Image34
2026-03-05 23:13:49,292 - app.services.file_processor - INFO -     ✅ Image 29 on page 1 done (29/62)
2026-03-05 23:13:49,294 - app.services.file_processor - INFO -   🤖 Calling Gemini Vision API (gemini-2.5-flash) for PDF_Page1_Image34...
2026-03-05 23:13:49,813 - app.main - INFO - ⏱  GET /dev/errors  →  200  3.1ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:13:52,297 - app.services.file_processor - INFO -   ✅ Gemini Vision analysis complete for PDF_Page1_Image32
2026-03-05 23:13:52,297 - app.services.file_processor - INFO - 🖼️  Processing image with gemini-2.5-flash: PDF_Page1_Image35
2026-03-05 23:13:52,297 - app.services.file_processor - INFO -     ✅ Image 32 on page 1 done (30/62)
2026-03-05 23:13:52,299 - app.services.file_processor - INFO -   🤖 Calling Gemini Vision API (gemini-2.5-flash) for PDF_Page1_Image35...
2026-03-05 23:13:53,810 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.2ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:13:55,082 - app.services.file_processor - INFO -   ✅ Gemini Vision analysis complete for PDF_Page1_Image33
2026-03-05 23:13:55,083 - app.services.file_processor - INFO - 🖼️  Processing image with gemini-2.5-flash: PDF_Page1_Image36
2026-03-05 23:13:55,084 - app.services.file_processor - INFO -     ✅ Image 33 on page 1 done (31/62)
2026-03-05 23:13:55,085 - app.services.file_processor - INFO -   🤖 Calling Gemini Vision API (gemini-2.5-flash) for PDF_Page1_Image36...
2026-03-05 23:13:57,808 - app.main - INFO - ⏱  GET /dev/errors  →  200  0.2ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:13:59,754 - app.services.file_processor - INFO -   ✅ Gemini Vision analysis complete for PDF_Page1_Image31
2026-03-05 23:13:59,756 - app.services.file_processor - INFO - 🖼️  Processing image with gemini-2.5-flash: PDF_Page1_Image37
2026-03-05 23:13:59,757 - app.services.file_processor - INFO -     ✅ Image 31 on page 1 done (32/62)
2026-03-05 23:13:59,761 - app.services.file_processor - INFO -   🤖 Calling Gemini Vision API (gemini-2.5-flash) for PDF_Page1_Image37...
2026-03-05 23:14:00,940 - app.services.file_processor - INFO -   ✅ Gemini Vision analysis complete for PDF_Page1_Image30
2026-03-05 23:14:00,940 - app.services.file_processor - INFO - 🖼️  Processing image with gemini-2.5-flash: PDF_Page1_Image38
2026-03-05 23:14:00,940 - app.services.file_processor - INFO -     ✅ Image 30 on page 1 done (33/62)
2026-03-05 23:14:00,941 - app.services.file_processor - INFO -   🤖 Calling Gemini Vision API (gemini-2.5-flash) for PDF_Page1_Image38...
2026-03-05 23:14:01,811 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.2ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:14:02,915 - app.services.file_processor - INFO -   ✅ Gemini Vision analysis complete for PDF_Page1_Image35
2026-03-05 23:14:02,915 - app.services.file_processor - INFO - 🖼️  Processing image with gemini-2.5-flash: PDF_Page1_Image39
2026-03-05 23:14:02,916 - app.services.file_processor - INFO -     ✅ Image 35 on page 1 done (34/62)
2026-03-05 23:14:02,918 - app.services.file_processor - INFO -   🤖 Calling Gemini Vision API (gemini-2.5-flash) for PDF_Page1_Image39...
2026-03-05 23:14:05,811 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.1ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:14:06,396 - app.services.file_processor - INFO -   ✅ Gemini Vision analysis complete for PDF_Page1_Image34
2026-03-05 23:14:06,396 - app.services.file_processor - INFO - 🖼️  Processing image with gemini-2.5-flash: PDF_Page1_Image40
2026-03-05 23:14:06,397 - app.services.file_processor - INFO -     ✅ Image 34 on page 1 done (35/62)
2026-03-05 23:14:06,401 - app.services.file_processor - INFO -   🤖 Calling Gemini Vision API (gemini-2.5-flash) for PDF_Page1_Image40...
2026-03-05 23:14:08,719 - app.services.file_processor - INFO -   ✅ Gemini Vision analysis complete for PDF_Page1_Image39
2026-03-05 23:14:08,719 - app.services.file_processor - INFO - 🖼️  Processing image with gemini-2.5-flash: PDF_Page1_Image41
2026-03-05 23:14:08,720 - app.services.file_processor - INFO -     ✅ Image 39 on page 1 done (36/62)
2026-03-05 23:14:08,724 - app.services.file_processor - INFO -   🤖 Calling Gemini Vision API (gemini-2.5-flash) for PDF_Page1_Image41...
2026-03-05 23:14:09,810 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.1ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:14:10,594 - app.services.file_processor - INFO -   ✅ Gemini Vision analysis complete for PDF_Page1_Image36
2026-03-05 23:14:10,595 - app.services.file_processor - INFO - 🖼️  Processing image with gemini-2.5-flash: PDF_Page1_Image42
2026-03-05 23:14:10,596 - app.services.file_processor - INFO -     ✅ Image 36 on page 1 done (37/62)
2026-03-05 23:14:10,600 - app.services.file_processor - INFO -   🤖 Calling Gemini Vision API (gemini-2.5-flash) for PDF_Page1_Image42...
2026-03-05 23:14:12,684 - app.services.file_processor - INFO -   ✅ Gemini Vision analysis complete for PDF_Page1_Image38
2026-03-05 23:14:12,684 - app.services.file_processor - INFO - 🖼️  Processing image with gemini-2.5-flash: PDF_Page1_Image43
2026-03-05 23:14:12,685 - app.services.file_processor - INFO -     ✅ Image 38 on page 1 done (38/62)
2026-03-05 23:14:12,689 - app.services.file_processor - INFO -   🤖 Calling Gemini Vision API (gemini-2.5-flash) for PDF_Page1_Image43...
2026-03-05 23:14:13,810 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.1ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:14:15,955 - app.services.file_processor - INFO -   ✅ Gemini Vision analysis complete for PDF_Page1_Image37
2026-03-05 23:14:15,955 - app.services.file_processor - INFO - 🖼️  Processing image with gemini-2.5-flash: PDF_Page1_Image44
2026-03-05 23:14:15,956 - app.services.file_processor - INFO -     ✅ Image 37 on page 1 done (39/62)
2026-03-05 23:14:15,960 - app.services.file_processor - INFO -   🤖 Calling Gemini Vision API (gemini-2.5-flash) for PDF_Page1_Image44...
2026-03-05 23:14:17,811 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.2ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:14:21,354 - app.services.file_processor - INFO -   ✅ Gemini Vision analysis complete for PDF_Page1_Image43
2026-03-05 23:14:21,355 - app.services.file_processor - INFO - 🖼️  Processing image with gemini-2.5-flash: PDF_Page1_Image45
2026-03-05 23:14:21,356 - app.services.file_processor - INFO -     ✅ Image 43 on page 1 done (40/62)
2026-03-05 23:14:21,360 - app.services.file_processor - INFO -   🤖 Calling Gemini Vision API (gemini-2.5-flash) for PDF_Page1_Image45...
2026-03-05 23:14:21,810 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.0ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:14:25,808 - app.main - INFO - ⏱  GET /dev/errors  →  200  0.7ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:14:26,155 - app.services.file_processor - INFO -   ✅ Gemini Vision analysis complete for PDF_Page1_Image40
2026-03-05 23:14:26,156 - app.services.file_processor - INFO - 🖼️  Processing image with gemini-2.5-flash: PDF_Page1_Image46
2026-03-05 23:14:26,157 - app.services.file_processor - INFO -     ✅ Image 40 on page 1 done (41/62)
2026-03-05 23:14:26,160 - app.services.file_processor - INFO -   🤖 Calling Gemini Vision API (gemini-2.5-flash) for PDF_Page1_Image46...
2026-03-05 23:14:28,296 - app.services.file_processor - INFO -   ✅ Gemini Vision analysis complete for PDF_Page1_Image42
2026-03-05 23:14:28,297 - app.services.file_processor - INFO - 🖼️  Processing image with gemini-2.5-flash: PDF_Page1_Image47
2026-03-05 23:14:28,297 - app.services.file_processor - INFO -     ✅ Image 42 on page 1 done (42/62)
2026-03-05 23:14:28,300 - app.services.file_processor - INFO -   🤖 Calling Gemini Vision API (gemini-2.5-flash) for PDF_Page1_Image47...
2026-03-05 23:14:29,370 - app.services.file_processor - INFO -   ✅ Gemini Vision analysis complete for PDF_Page1_Image41
2026-03-05 23:14:29,371 - app.services.file_processor - INFO - 🖼️  Processing image with gemini-2.5-flash: PDF_Page1_Image48
2026-03-05 23:14:29,372 - app.services.file_processor - INFO -   🤖 Calling Gemini Vision API (gemini-2.5-flash) for PDF_Page1_Image48...
2026-03-05 23:14:29,373 - app.services.file_processor - INFO -     ✅ Image 41 on page 1 done (43/62)
2026-03-05 23:14:29,809 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.1ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:14:30,353 - app.services.file_processor - INFO -   ✅ Gemini Vision analysis complete for PDF_Page1_Image44
2026-03-05 23:14:30,353 - app.services.file_processor - INFO - 🖼️  Processing image with gemini-2.5-flash: PDF_Page1_Image49
2026-03-05 23:14:30,354 - app.services.file_processor - INFO -     ✅ Image 44 on page 1 done (44/62)
2026-03-05 23:14:30,355 - app.services.file_processor - INFO -   🤖 Calling Gemini Vision API (gemini-2.5-flash) for PDF_Page1_Image49...
2026-03-05 23:14:33,812 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.8ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:14:37,475 - app.services.file_processor - INFO -   ✅ Gemini Vision analysis complete for PDF_Page1_Image45
2026-03-05 23:14:37,476 - app.services.file_processor - INFO - 🖼️  Processing image with gemini-2.5-flash: PDF_Page1_Image50
2026-03-05 23:14:37,476 - app.services.file_processor - INFO -     ✅ Image 45 on page 1 done (45/62)
2026-03-05 23:14:37,479 - app.services.file_processor - INFO -   🤖 Calling Gemini Vision API (gemini-2.5-flash) for PDF_Page1_Image50...
2026-03-05 23:14:37,810 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.1ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:14:41,057 - app.services.file_processor - INFO -   ✅ Gemini Vision analysis complete for PDF_Page1_Image46
2026-03-05 23:14:41,059 - app.services.file_processor - INFO -     ✅ Image 46 on page 1 done (46/62)
2026-03-05 23:14:41,811 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.2ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:14:45,284 - app.services.file_processor - INFO -   ✅ Gemini Vision analysis complete for PDF_Page1_Image49
2026-03-05 23:14:45,286 - app.services.file_processor - INFO -     ✅ Image 49 on page 1 done (47/62)
2026-03-05 23:14:45,290 - app.services.file_processor - INFO -   ✅ Gemini Vision analysis complete for PDF_Page1_Image47
2026-03-05 23:14:45,470 - app.services.file_processor - INFO -     ✅ Image 47 on page 1 done (48/62)
2026-03-05 23:14:45,810 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.0ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:14:47,841 - app.services.file_processor - INFO -   ✅ Gemini Vision analysis complete for PDF_Page1_Image50
2026-03-05 23:14:47,842 - app.services.file_processor - INFO -     ✅ Image 50 on page 1 done (49/62)
2026-03-05 23:14:49,809 - app.main - INFO - ⏱  GET /dev/errors  →  200  0.9ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:14:53,810 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.0ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:14:57,810 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.1ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:14:58,476 - app.services.file_processor - INFO -   ✅ Gemini Vision analysis complete for PDF_Page1_Image48
2026-03-05 23:14:58,479 - app.services.file_processor - INFO -     ✅ Image 48 on page 1 done (50/62)
2026-03-05 23:14:58,680 - app.services.file_processor - INFO -   🚚 Processing image batch 2/2 (12 images, workers=5)
2026-03-05 23:14:58,681 - app.services.file_processor - INFO - 🖼️  Processing image with gemini-2.5-flash: PDF_Page1_Image51
2026-03-05 23:14:58,681 - app.services.file_processor - INFO - 🖼️  Processing image with gemini-2.5-flash: PDF_Page1_Image52
2026-03-05 23:14:58,682 - app.services.file_processor - INFO - 🖼️  Processing image with gemini-2.5-flash: PDF_Page1_Image53
2026-03-05 23:14:58,682 - app.services.file_processor - INFO - 🖼️  Processing image with gemini-2.5-flash: PDF_Page1_Image54
2026-03-05 23:14:58,683 - app.services.file_processor - INFO -   🤖 Calling Gemini Vision API (gemini-2.5-flash) for PDF_Page1_Image51...
2026-03-05 23:14:58,684 - app.services.file_processor - INFO -   🤖 Calling Gemini Vision API (gemini-2.5-flash) for PDF_Page1_Image52...
2026-03-05 23:14:58,684 - app.services.file_processor - INFO - 🖼️  Processing image with gemini-2.5-flash: PDF_Page1_Image55
2026-03-05 23:14:58,685 - app.services.file_processor - INFO -   🤖 Calling Gemini Vision API (gemini-2.5-flash) for PDF_Page1_Image53...
2026-03-05 23:14:58,686 - app.services.file_processor - INFO -   🤖 Calling Gemini Vision API (gemini-2.5-flash) for PDF_Page1_Image54...
2026-03-05 23:14:58,690 - app.services.file_processor - INFO -   🤖 Calling Gemini Vision API (gemini-2.5-flash) for PDF_Page1_Image55...
2026-03-05 23:15:01,809 - app.main - INFO - ⏱  GET /dev/errors  →  200  0.9ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:15:05,811 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.0ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:15:08,064 - app.services.file_processor - INFO -   ✅ Gemini Vision analysis complete for PDF_Page1_Image51
2026-03-05 23:15:08,065 - app.services.file_processor - INFO - 🖼️  Processing image with gemini-2.5-flash: PDF_Page1_Image56
2026-03-05 23:15:08,066 - app.services.file_processor - INFO -     ✅ Image 51 on page 1 done (51/62)
2026-03-05 23:15:08,070 - app.services.file_processor - INFO -   🤖 Calling Gemini Vision API (gemini-2.5-flash) for PDF_Page1_Image56...
2026-03-05 23:15:09,810 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.1ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:15:12,072 - app.services.file_processor - INFO -   ✅ Gemini Vision analysis complete for PDF_Page1_Image55
2026-03-05 23:15:12,073 - app.services.file_processor - INFO - 🖼️  Processing image with gemini-2.5-flash: PDF_Page1_Image57
2026-03-05 23:15:12,074 - app.services.file_processor - INFO -     ✅ Image 55 on page 1 done (52/62)
2026-03-05 23:15:12,078 - app.services.file_processor - INFO -   🤖 Calling Gemini Vision API (gemini-2.5-flash) for PDF_Page1_Image57...
2026-03-05 23:15:13,810 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.2ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:15:15,551 - app.services.file_processor - INFO -   ✅ Gemini Vision analysis complete for PDF_Page1_Image52
2026-03-05 23:15:15,552 - app.services.file_processor - INFO - 🖼️  Processing image with gemini-2.5-flash: PDF_Page1_Image58
2026-03-05 23:15:15,553 - app.services.file_processor - INFO -     ✅ Image 52 on page 1 done (53/62)
2026-03-05 23:15:15,556 - app.services.file_processor - INFO -   🤖 Calling Gemini Vision API (gemini-2.5-flash) for PDF_Page1_Image58...
2026-03-05 23:15:17,810 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.1ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:15:18,596 - app.services.file_processor - INFO -   ✅ Gemini Vision analysis complete for PDF_Page1_Image53
2026-03-05 23:15:18,597 - app.services.file_processor - INFO - 🖼️  Processing image with gemini-2.5-flash: PDF_Page1_Image59
2026-03-05 23:15:18,597 - app.services.file_processor - INFO -     ✅ Image 53 on page 1 done (54/62)
2026-03-05 23:15:18,601 - app.services.file_processor - INFO -   🤖 Calling Gemini Vision API (gemini-2.5-flash) for PDF_Page1_Image59...
2026-03-05 23:15:18,794 - app.services.file_processor - INFO -   ✅ Gemini Vision analysis complete for PDF_Page1_Image54
2026-03-05 23:15:18,798 - app.services.file_processor - INFO - 🖼️  Processing image with gemini-2.5-flash: PDF_Page1_Image60
2026-03-05 23:15:18,800 - app.services.file_processor - INFO -   🤖 Calling Gemini Vision API (gemini-2.5-flash) for PDF_Page1_Image60...
2026-03-05 23:15:18,833 - app.services.file_processor - INFO -     ✅ Image 54 on page 1 done (55/62)
2026-03-05 23:15:21,812 - app.main - INFO - ⏱  GET /dev/errors  →  200  3.2ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:15:25,810 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.0ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:15:27,729 - app.services.file_processor - INFO -   ✅ Gemini Vision analysis complete for PDF_Page1_Image56
2026-03-05 23:15:27,730 - app.services.file_processor - INFO - 🖼️  Processing image with gemini-2.5-flash: PDF_Page1_Image61
2026-03-05 23:15:27,731 - app.services.file_processor - INFO -     ✅ Image 56 on page 1 done (56/62)
2026-03-05 23:15:27,735 - app.services.file_processor - INFO -   🤖 Calling Gemini Vision API (gemini-2.5-flash) for PDF_Page1_Image61...
2026-03-05 23:15:29,809 - app.main - INFO - ⏱  GET /dev/errors  →  200  0.9ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:15:30,327 - app.services.file_processor - INFO -   ✅ Gemini Vision analysis complete for PDF_Page1_Image58
2026-03-05 23:15:30,328 - app.services.file_processor - INFO - 🖼️  Processing image with gemini-2.5-flash: PDF_Page1_Image62
2026-03-05 23:15:30,329 - app.services.file_processor - INFO -     ✅ Image 58 on page 1 done (57/62)
2026-03-05 23:15:30,333 - app.services.file_processor - INFO -   🤖 Calling Gemini Vision API (gemini-2.5-flash) for PDF_Page1_Image62...
2026-03-05 23:15:30,710 - app.services.file_processor - INFO -   ✅ Gemini Vision analysis complete for PDF_Page1_Image57
2026-03-05 23:15:30,711 - app.services.file_processor - INFO -     ✅ Image 57 on page 1 done (58/62)
2026-03-05 23:15:31,205 - app.services.file_processor - INFO -   ✅ Gemini Vision analysis complete for PDF_Page1_Image59
2026-03-05 23:15:31,206 - app.services.file_processor - INFO -     ✅ Image 59 on page 1 done (59/62)
2026-03-05 23:15:31,704 - app.services.file_processor - INFO -   ✅ Gemini Vision analysis complete for PDF_Page1_Image60
2026-03-05 23:15:31,705 - app.services.file_processor - INFO -     ✅ Image 60 on page 1 done (60/62)
2026-03-05 23:15:33,810 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.1ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:15:37,810 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.1ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:15:40,618 - app.services.file_processor - INFO -   ✅ Gemini Vision analysis complete for PDF_Page1_Image62
2026-03-05 23:15:40,619 - app.services.file_processor - INFO -     ✅ Image 62 on page 1 done (61/62)
2026-03-05 23:15:41,809 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.0ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:15:45,810 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.1ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:15:49,810 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.0ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:15:53,200 - app.services.file_processor - INFO -   ✅ Gemini Vision analysis complete for PDF_Page1_Image61
2026-03-05 23:15:53,201 - app.services.file_processor - INFO -     ✅ Image 61 on page 1 done (62/62)
2026-03-05 23:15:53,388 - app.services.file_processor - INFO -   ✅ PDF processed: 1 pages, 62 images extracted (PARALLEL)
2026-03-05 23:15:53,394 - app.routers.files - INFO -   ✅ Text extracted: 365399 chars, 55895 words
2026-03-05 23:15:53,395 - app.routers.files - INFO - 📈 Progress stage completed: file_id=c124ede1-ae3c-40df-8816-13a7ef6214a9 stage=image_ocr duration=232.29s
2026-03-05 23:15:53,395 - app.routers.files - INFO - 📈 Progress stage transition: file_id=c124ede1-ae3c-40df-8816-13a7ef6214a9 stage=extracting percent=25.00
2026-03-05 23:15:53,593 - app.routers.files - INFO -   3️⃣  Creating text chunks...
2026-03-05 23:15:53,593 - app.routers.files - INFO - 📈 Progress stage completed: file_id=c124ede1-ae3c-40df-8816-13a7ef6214a9 stage=extracting duration=0.20s
2026-03-05 23:15:53,593 - app.routers.files - INFO - 📈 Progress stage transition: file_id=c124ede1-ae3c-40df-8816-13a7ef6214a9 stage=chunking percent=55.00
2026-03-05 23:15:53,810 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.1ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:15:53,936 - app.routers.files - INFO -   ✅ Created 559 chunks
2026-03-05 23:15:54,123 - app.routers.files - INFO -   4️⃣  Generating embeddings for 559 chunks...
2026-03-05 23:15:54,124 - app.routers.files - INFO - 📈 Progress stage completed: file_id=c124ede1-ae3c-40df-8816-13a7ef6214a9 stage=chunking duration=0.53s
2026-03-05 23:15:54,124 - app.routers.files - INFO - 📈 Progress stage transition: file_id=c124ede1-ae3c-40df-8816-13a7ef6214a9 stage=embedding percent=65.00
2026-03-05 23:15:54,313 - app.services.file_processor - INFO - 🔢 Generating 559 embeddings in batch (Voyage AI)...
2026-03-05 23:15:57,089 - app.services.file_processor - INFO - ✅ Generated 559 embeddings successfully
2026-03-05 23:15:57,812 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.8ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:16:01,810 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.1ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:16:05,810 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.1ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:16:09,809 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.1ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:16:13,810 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.1ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:16:17,810 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.3ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:16:21,812 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.0ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:16:25,810 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.2ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:16:29,809 - app.main - INFO - ⏱  GET /dev/errors  →  200  0.8ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:16:33,810 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.3ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:16:37,810 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.3ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:16:41,810 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.1ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:16:45,809 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.1ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:16:49,810 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.2ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:16:53,809 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.1ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:16:54,156 - app.routers.files - INFO -   5️⃣  Storing chunks in database...
2026-03-05 23:16:54,156 - app.routers.files - INFO - 📈 Progress stage completed: file_id=c124ede1-ae3c-40df-8816-13a7ef6214a9 stage=embedding duration=60.03s
2026-03-05 23:16:54,156 - app.routers.files - INFO - 📈 Progress stage transition: file_id=c124ede1-ae3c-40df-8816-13a7ef6214a9 stage=storing percent=85.00
2026-03-05 23:16:57,810 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.1ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:17:01,809 - app.main - INFO - ⏱  GET /dev/errors  →  200  0.9ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:17:05,811 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.3ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:17:09,810 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.2ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:17:13,810 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.1ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:17:17,810 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.0ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:17:21,810 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.1ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:17:25,810 - app.main - INFO - ⏱  GET /dev/errors  →  200  0.9ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:17:29,808 - app.main - INFO - ⏱  GET /dev/errors  →  200  0.7ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:17:33,810 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.1ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:17:37,810 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.1ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:17:41,810 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.1ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:17:45,812 - app.main - INFO - ⏱  GET /dev/errors  →  200  3.0ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:17:49,809 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.1ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:17:53,810 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.1ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:17:57,810 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.0ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:18:00,236 - tracer - INFO - [660f4fe4] START GET /api/buckets/{id}/conversations  user_id=48c4c78c-bdfb-41b0-85d1-cadd60b9c555 bucket_id=e7e5c7df-7bcf-481d-8115-a97bf3ac8bc3
2026-03-05 23:18:00,806 - tracer - INFO - [660f4fe4]   🟢 get_effective_user_id  570.1ms (total 570.1ms)  
2026-03-05 23:18:00,866 - app.routers.files - INFO -   ✅ Stored 559 chunks
2026-03-05 23:18:01,121 - tracer - INFO - [660f4fe4]   🟢 DB verify bucket  315.1ms (total 885.2ms)  
2026-03-05 23:18:01,148 - app.routers.files - INFO -   6️⃣  Generating spatial summary...
2026-03-05 23:18:01,148 - app.routers.files - INFO - 📈 Progress stage completed: file_id=c124ede1-ae3c-40df-8816-13a7ef6214a9 stage=storing duration=66.99s
2026-03-05 23:18:01,148 - app.routers.files - INFO - 📈 Progress stage transition: file_id=c124ede1-ae3c-40df-8816-13a7ef6214a9 stage=summarizing percent=95.00
2026-03-05 23:18:01,399 - app.services.file_processor - INFO - 📄 Generating spatial summary: 1 pages in parallel for 'norseorganic page.pdf'
2026-03-05 23:18:01,400 - tracer - INFO - [660f4fe4]   🟢 DB query conversations  279.2ms (total 1164.4ms)  count=1
2026-03-05 23:18:01,402 - tracer - INFO - [660f4fe4] END GET /api/buckets/{id}/conversations  OK 200  1166.7ms  🟡  steps=3  slowest=get_effective_user_id(570.1ms)
2026-03-05 23:18:01,403 - app.main - WARNING - ⏱  GET /api/buckets/e7e5c7df-7bcf-481d-8115-a97bf3ac8bc3/conversations  →  200  1169.3ms  🟡 SLOW
INFO:     127.0.0.1:60980 - "GET /api/buckets/e7e5c7df-7bcf-481d-8115-a97bf3ac8bc3/conversations HTTP/1.1" 200 OK
2026-03-05 23:18:01,809 - app.main - INFO - ⏱  GET /dev/errors  →  200  0.6ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:18:05,809 - app.main - INFO - ⏱  GET /dev/errors  →  200  0.9ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:18:09,809 - app.main - INFO - ⏱  GET /dev/errors  →  200  0.7ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:18:13,810 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.0ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:18:17,809 - app.main - INFO - ⏱  GET /dev/errors  →  200  0.9ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:18:21,809 - app.main - INFO - ⏱  GET /dev/errors  →  200  0.9ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:18:25,810 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.3ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:18:29,809 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.0ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:18:33,810 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.2ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:18:37,809 - app.main - INFO - ⏱  GET /dev/errors  →  200  0.8ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:18:41,809 - app.main - INFO - ⏱  GET /dev/errors  →  200  0.9ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:18:45,809 - app.main - INFO - ⏱  GET /dev/errors  →  200  0.8ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:18:49,809 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.2ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:18:53,809 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.1ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:18:57,809 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.0ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:19:01,810 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.5ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:19:05,810 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.2ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:19:09,809 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.1ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:19:13,810 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.4ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:19:17,811 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.3ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:19:21,810 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.3ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:19:25,810 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.0ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:19:29,810 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.2ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:19:33,810 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.1ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:19:37,809 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.0ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:19:41,810 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.3ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:19:43,599 - app.services.file_processor - INFO -   ✅ Page 1/1 summary done
2026-03-05 23:19:43,600 - app.services.file_processor - INFO - ✅ Spatial summary complete: 7856 chars across 1 pages
2026-03-05 23:19:43,600 - app.routers.files - WARNING - Web enrichment skipped: There is no current event loop in thread 'AnyIO worker thread'.
2026-03-05 23:19:44,448 - app.routers.files - INFO -   ✅ Summary stored (7856 chars)
2026-03-05 23:19:44,733 - app.routers.files - INFO - 📈 Progress stage completed: file_id=c124ede1-ae3c-40df-8816-13a7ef6214a9 stage=summarizing duration=103.58s
2026-03-05 23:19:44,733 - app.routers.files - INFO - 📈 Progress stage transition: file_id=c124ede1-ae3c-40df-8816-13a7ef6214a9 stage=finalizing percent=100.00
2026-03-05 23:19:45,810 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.1ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:19:46,586 - app.routers.files - INFO - 📈 Progress stage completed: file_id=c124ede1-ae3c-40df-8816-13a7ef6214a9 stage=finalizing duration=1.85s
2026-03-05 23:19:46,587 - app.routers.files - INFO - 📈 Progress stage transition: file_id=c124ede1-ae3c-40df-8816-13a7ef6214a9 stage=ready percent=100.00
2026-03-05 23:19:46,803 - app.routers.files - INFO - ✅ BACKGROUND PROCESSING COMPLETE: norseorganic page.pdf
2026-03-05 23:19:46,803 - app.routers.files - INFO - ================================================================================
2026-03-05 23:19:47,030 - app.services.notifications - INFO - ✅ Notification created for user 48c4c78c-bdfb-41b0-85d1-cadd60b9c555: File Processed
2026-03-05 23:19:49,810 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.1ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:19:53,810 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.4ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:19:57,809 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.1ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:20:01,809 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.3ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:20:05,810 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.4ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:20:09,807 - app.main - INFO - ⏱  GET /dev/errors  →  200  0.8ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:20:13,809 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.0ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:20:17,810 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.0ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:20:21,811 - app.main - INFO - ⏱  GET /dev/errors  →  200  2.6ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:20:25,810 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.6ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:20:29,829 - app.main - INFO - ⏱  GET /dev/errors  →  200  4.9ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:20:33,809 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.3ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:20:37,809 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.4ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:20:41,809 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.0ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:20:45,809 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.0ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:20:49,810 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.3ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:20:53,809 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.0ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:20:57,810 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.1ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:21:01,809 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.3ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:21:05,808 - app.main - INFO - ⏱  GET /dev/errors  →  200  0.7ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:21:09,808 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.2ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:21:13,807 - app.main - INFO - ⏱  GET /dev/errors  →  200  0.5ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:21:17,810 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.2ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:21:21,810 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.3ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:21:25,808 - app.main - INFO - ⏱  GET /dev/errors  →  200  0.7ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2026-03-05 23:21:29,809 - app.main - INFO - ⏱  GET /dev/errors  →  200  1.2ms  🟢
INFO:     127.0.0.1:60980 - "GET /dev/errors?limit=50 HTTP/1.1" 200 OK
2