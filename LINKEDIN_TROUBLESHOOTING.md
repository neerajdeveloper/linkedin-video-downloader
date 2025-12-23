# LinkedIn Video Extraction Troubleshooting

## Common Issues & Solutions

### Issue: "Unable to extract video"

This error typically occurs when:

1. **Video is Private/Restricted**
   - The video requires LinkedIn login
   - The video is only visible to connections
   - The video is company-restricted

2. **LinkedIn Changed Format**
   - LinkedIn occasionally updates their video structure
   - yt-dlp needs to be updated (we check this automatically)

3. **Authentication Required**
   - Some videos require being logged into LinkedIn
   - The video URL might be expired or invalid

## Solutions

### ✅ Try These First:

1. **Verify Video is Public**
   - Open the LinkedIn post in an incognito/private window
   - If you can't see it, it's likely private

2. **Check URL Format**
   - Make sure you're using the full LinkedIn post URL
   - Format: `https://www.linkedin.com/posts/...`

3. **Try Different Video**
   - Test with a known public LinkedIn video
   - Some videos simply can't be extracted

### 🔧 Advanced Solutions:

#### Option 1: Use LinkedIn Cookies (if video requires login)

If you need to extract videos that require login:

1. **Export cookies from browser:**
   - Install browser extension: "Get cookies.txt LOCALLY"
   - Log into LinkedIn
   - Export cookies to `cookies.txt`

2. **Use cookies with yt-dlp:**
   ```bash
   yt-dlp --cookies cookies.txt "LINKEDIN_URL"
   ```

#### Option 2: Update yt-dlp

We automatically check for updates, but you can manually update:

```bash
yt-dlp -U
```

#### Option 3: Check Video Accessibility

- Make sure the video plays in your browser
- Check if it's a native LinkedIn video (not embedded YouTube/Vimeo)
- Verify the post hasn't been deleted

## Error Messages Explained

### "Unable to extract video"
- **Meaning:** yt-dlp couldn't find the video in the LinkedIn post
- **Cause:** Private video, changed format, or invalid URL
- **Solution:** Try a different video or check if it's public

### "Private video"
- **Meaning:** Video requires authentication
- **Cause:** Video is restricted to connections or company
- **Solution:** Use cookies or try a public video

### "Request timed out"
- **Meaning:** LinkedIn took too long to respond
- **Cause:** Network issues or LinkedIn being slow
- **Solution:** Try again, check your internet connection

## What We've Improved

✅ **Multiple extraction methods** - Tries 3 different approaches
✅ **Better error messages** - More helpful feedback
✅ **Automatic yt-dlp updates** - Always uses latest version
✅ **Fallback methods** - Tries alternative extraction if first fails

## Still Having Issues?

1. **Check yt-dlp version:**
   ```bash
   yt-dlp --version
   ```

2. **Test directly with yt-dlp:**
   ```bash
   yt-dlp --dump-json "YOUR_LINKEDIN_URL"
   ```

3. **Report the issue:**
   - Include the LinkedIn URL
   - Include the error message
   - Check if video is public/private

## Tips for Best Results

✅ Use **public LinkedIn videos** (visible without login)
✅ Use **full post URLs** (not shortened links)
✅ Make sure video is **native LinkedIn** (not embedded)
✅ Try during **off-peak hours** (LinkedIn may be slower)

---

**Note:** Some LinkedIn videos simply cannot be extracted due to privacy restrictions or LinkedIn's terms of service. This is a limitation of the platform, not our tool.

