## FeedCloud  
This project is powered by python3.9, Django, DRF, Postgres, Redis, Celery, Rabbitmq.
  
## How to run it?
To make your review easier I provided a file named `.env.sample`,
you should set required environment variables inside it first.
I set some predefined values, you can give them a try.
>**HINT: The `EMAIL_HOST_PASSWORD` inside `.env.sample` is fake
> In case you want to test registration and email sending,
> use the one I sent from email. :)**

then you just need to rename it to `.env`.

>**CAUTION**: This isn't a good practice to have such a file in your repository,  
but I added it, to make your review easier! A better way could be using `--build-arg`.

Now you need to build your images
`docker-compose build --build-arg SECRET_KEY="MySup3rH@rDS3CR3T"`.
after building your images, you can simply run project with `docker-compose up`,

`Postgres` will persist its data on your local drive,
so you won't lose your data between `up` and `down`.
If you don't want this feature just remove `postgresql-data` in `docker-compose.yaml`.

Also  `Django` persist its static files on your local drive and `nginx` serve it from there.
## Initial Data  
To help your reviewing I added a django command management.  
After running the project you can run  
`docker-compose exec feedcloud python manage.py initdata`.  
It creates a superuser, you can read its email and password from `.env`.  
Also, it adds 2 feeds for start.  
  
The project is listening on `http://localhost:8008/`,  
you can send request to it by `curl`, `postman` or other applications  
but there is a `swagger` endpoint too. ِYou can get to know APIs   
and also use `swagger` to check APIs.  
  
## Authorization  
`JWT token` is used for authorization.  
You can get it from `/users/login` with email & password.  
Also, you can refresh your token from `/users/refresh_token`.  
After getting your `JWT token` from `login` endpoint or `refresh_token` endpoint,  
you can set it in your `Authorization` request header with `JWT this.my.jwt` format.  
>Be aware, to refresh your token you should have a valid token!  
  
## API versioning  
To support later changes we have API versioning.  
Current version is `1.0` and it's the default version too.  
You can change it to other versions with setting `Accept` request header.  
For example `Accept application/json;version=2.0`  
  
## Background Tasks  
This project has 4 background tasks:  
  
- `fetch_feed_entries`  
  fetch feed entries and save them, called by `update_feed` signal  
- `schedule_fetch_feed_batch`   
    fetch feeds batch by batch, called by `celery beat`  
- `send_email`  
  send an email with one time confirmation link  
- `update_api_permissions`  
  
  update permissions list to handle permissions of staffs,  
  you can manage them from `django admin`  
  
## CORS Test  
Huh, you have been CORSed! Add your desired url in `CORS_ALLOWED_ORIGINS` and test it with  
  
    curl -H "Origin: http://localhost:3000" --header 'Authorization: JWT token' -v -X OPTIONS https://apid.send.cloud/feeds  
## Django Admin  
Login to `localhost:8008/admin` to manage user, staffs and much more!  

## Email confirmation
After registration, project sends an email containing a one-time link to confirm registration.
> **CAUTION** It's not a good practice to have `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD`
> inside repository. But it's a test account on gmail for reviewing purpose!

>**TIP**: If you used this project in your environment,
> you should add the port to the link confirmation you received in your email.
> Your link should look like this:
>`http://localhost:8008/users/approve_email/token1/token2`
  
## Translation  
This project supports 3 languages, but not completely!  
It was hard to translate all messages :) but we have the base of translation.  
Default language is `en` but project also supports `du` and `fa`.  
You can get your desired language with setting  
`Accept-Language` header request to one of the supported languages.  
  
## Timezone  
To support users from different timezones, project supports timezones too.  
Default timezone is `UTC` but you can get times in your desired timezone with  
setting `Timezone` header request to your timezone.  
For example `Asia/Tehran` or `Europe/Amsterdam`.  
>Use `import pytz; pytz.all_timezones` in `python shell` to list all supported timezones.  
  
## Tests  
TDD is a good practice. We have some unit and functional tests.
Set your desired variables inside `.env.test`. You just need check `redis server` configs.
After successfully running `docker-compose up -d`
You can test project with running
`docker-compose exec --env DJANGO_SETTINGS_MODULE="feedcloud.settings.testing" feedcloud pytest`
in the root of project and hope they pass. :)
  
## Throttling  
This project has a customized throttling class `CustomViewRateThrottle`
inherited from `DRF throttling`.
You can change `throttle_rate` in each `view class`.
Example `10/day`, `20/hour`.
Staff users are free to use endpoints as much as they want.
This throttling class also works on authenticated and
non-authenticated users (base on IP address) separately.

## Responses Structure  
All the responses have a structured content based on success or error.  
  
- Success response  
  
      {  
		 "data": list or dict,
		 "message": str,
		 "show_type": str,
		 "current_time": int, server response epoch (unix) time
		 "success": true,
		 "index": int,
		 "total": int
	  }  
- Error response  
  
      {  
         "message": str or list, # Error message
         "show_type": str,
         "current_time": int, server response epoch (unix) time
         "success": false
      }

## Assignment abilities
- Follow and unfollow feeds
	- follow 
		`POST` request to `http://localhost:8008/feeds/followed`
		**body** `{"id": feed_id}`
	- unfollow
	    `DELETE` request to `http://localhost:8008/feeds/followed/{feed_id}`
- List feeds registered by them
	`GET` request to `http://localhost:8008/feeds/my_feeds`
- List all feeds 
	`GET` request to `http://localhost:8008/feeds`
- List entries belong to one feed
	`GET` request to `http://localhost:8008/feeds/{feed_id}/entries`
- Mark entry as read
	`POST` request to `http://localhost:8008/entries/read`
	**body** `{"id": entry_id}`
- Filter read/unread feed entries per feed and globally
	- entries per feed
		- Read
			`GET` request to `http://localhost:8008/feeds/{feed_id}/entries?read=true`
		- Unread
			`GET` request to `http://localhost:8008/feeds/{feed_id}/entries?read=false`
	- entries globally
			- Read
				`GET` request to `http://localhost:8008/entries?read=true`
			- Unread
				`GET` request to `http://localhost:8008/entries?read=false`
- Force feed update
	- Just force it!
		`PATCH` request to `http://localhost:8008/feeds/{feed_id}`
		**body** `{"force_update": true}`
   - Update feed link
	   `PATCH` request to `http://localhost:8008/feeds/{feed_id}`
		**body** `{"link": "you-new.link"}`
- Periodically task and back-off mechanism
  - Each Feed has a field named `status`
	- Active
 	  Feeds that are fetched before and are working fine.
	- Pending
	  Feeds that are recently created or updated and didn't fetch till now.
	- Error 
	  Feeds that had an error during fetching entries.
   - Each Feed has a field named `priority`
     - High 
     - Low
     - STOP
	   
     Each success in fetching of entries leads to increasing the priority and
     of course each fail in fetching of entries leads to decreasing the priority.
     Based on this, each feed after 2 fails goes to `Error` status, 
     and an admin should check the logs!
     `schedule_fetch_feed_batch` works periodically and
     tries to fetch `HIGH` priority feeds every 2nd minute and
     `LOW` priority feeds every 5th minute.
	 In case you want to schedule it faster or slower,
	 change `schedule` of `beat_schedule` in `feedcloud/feedcloud/celery.py`.
	 I set these times to fasten your review,
	 but I believe in production we should use longer periods.
