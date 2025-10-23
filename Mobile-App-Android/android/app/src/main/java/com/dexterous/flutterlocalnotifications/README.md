# Flutter Local Notifications Patch

This directory contains a patch file for the flutter_local_notifications package to fix an issue with ambiguous method calls in the Android implementation.

## Issue

When building the app with Flutter 3.24 or newer, you may encounter the following error:

```
error: reference to bigLargeIcon is ambiguous
bigPictureStyle.bigLargeIcon(null);
                     ^
both method bigLargeIcon(Bitmap) in BigPictureStyle and method bigLargeIcon(Icon) in BigPictureStyle match
```

## Solution

The patch file `FlutterLocalNotificationsPlugin.java.patch` fixes this issue by explicitly casting the null value to a Bitmap:

```java
// Before
bigPictureStyle.bigLargeIcon(null);

// After
bigPictureStyle.bigLargeIcon((android.graphics.Bitmap) null);
```

## How to Apply the Patch

1. Find the location of the flutter_local_notifications package in your Flutter cache:
   ```
   $HOME/.pub-cache/hosted/pub.dev/flutter_local_notifications-X.Y.Z/android/src/main/java/com/dexterous/flutterlocalnotifications/
   ```
   (On Windows, this would be in `%LOCALAPPDATA%\Pub\Cache\hosted\pub.dev\flutter_local_notifications-X.Y.Z\...`)

2. Apply the patch to the FlutterLocalNotificationsPlugin.java file:
   ```
   patch FlutterLocalNotificationsPlugin.java < FlutterLocalNotificationsPlugin.java.patch
   ```

3. Rebuild your app.

## Alternative Solution

Instead of patching the package, you can also:

1. Create a copy of the FlutterLocalNotificationsPlugin.java file in your app's Android source directory (this directory)
2. Apply the fix manually
3. Rebuild your app

The Android build system will use your local copy of the file instead of the one from the package.

## References

This fix is based on the pull request in the flutter_local_notifications repository:
https://github.com/MaikuB/flutter_local_notifications/pull/2355
