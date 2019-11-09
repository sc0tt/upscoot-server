# Upscoot

Upscoot is a service to upload images. I use this to upload my own files to share with other people.

This repository is the backend of the service. It is currently written in Python using Flask.

#### The planned features are:

 * Upload by File or URL
 * Create 'hidden' files which don't show up in the normal listing
 * 'hop' functionality to see (public) files uploaded on this day in previous years
 * 'list' get a json object of all the (public) files
 * 'rand' view a random (public) upload
 * Upload images to S3 or some other cloud storage
 * Create Docker containers
 * Tests
 * CI
 * Coverage
 * Android app to upload files easily through your phone
 * Custom groups, so anyone could create their own group by using their own password
 * Group pages to see all images for a group
 * Rand, hop, and list for group images
 * Group moderation
 * Group support for the Android app
 
I intend to also open source the android application once the server is functional. 
 
The current implementation of Upscoot supports most of these things in a very primitive way. This project is an attempt
at creating a more reliable, testable, and reusable website. 

[View on Github](https://github.com/sc0tt/upscoot-server)