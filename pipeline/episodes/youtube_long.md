# How full-length videos get to YouTube

Buffer can only post YouTube **Shorts**, so long videos (episodes and weekly compilations) need another route.

## Automatic route: Metricool (needs a one-time setup by the user)
1. Load the Metricool tools and call `getBrandSettings`.
2. Look for a brand whose `networksData.youtubeData` is **UC5b7O0EUwmnb-w8GPGuV2gw** (the Honey Bunny Kidz channel).
   - The existing brand 7599584 ("වටේ") is a DIFFERENT channel (UCglQy…). **Never post Honey Bunny videos to it.**
3. If the Honey Bunny brand exists, schedule the long video with `createScheduledPost`:
   blogId = that brand's id; media [raw.githubusercontent.com video URL]; providers [{"network":"youtube"}];
   publicationDate {dateTime, timezone "Asia/Colombo"}; youtubeData {"title", "type":"video", "privacy":"public",
   "tags":[...], "category":"FILM_ANIMATION" (or "EDUCATION" for LEARN/FACT), "madeForKids":true, "isAiGeneratedContent":true};
   videoThumbnailUrl = the landscape thumbnail URL; text = the YouTube description; autoPublish true.
   Check the response media URL points to static.metricool.com before the file is deleted from GitHub.
   Record the Metricool post id in log.json as "metricool_youtube_long".
4. If there is no such brand (setup not done yet), list the video in the summary as "upload manually to YouTube Studio"
   with title, description, tags, video link and thumbnail link (the old way).

## One-time setup (user)
In Metricool, add a new brand "Honey Bunny Kidz" and connect the Honey Bunny Kidz YouTube channel
(and optionally the Facebook page). If the Metricool plan only allows one brand, keep uploading by hand.
