#!/bin/python3
from os import path
import configparser
import praw

dope_title = """
__________                __                   __   
\______   \_____    _____/  |_  ____   _______/  |_ 
 |     ___/\__  \  /  _ \   __\/ __ \ /  ___/\   __\\
 |    |     / __ \(  <_> )  | \  ___/ \___ \  |  |  
 |____|    (____  /\____/|__|  \___  >____  > |__|  
                \/                 \/     \/        
Clean out your reddit posts!

"""

def parse_config(config_file):
    """ Accepts INI file, returns reddit credentials(dict), mentionbot settings(dict)"""
    config = configparser.SafeConfigParser()
    config.read(config_file)
    return config['reddit_creds'], config['paotester']

def reddit_login(creds):
    reddit = praw.Reddit(
        client_id = creds['client_id'],
        client_secret = creds['client_secret'],
        user_agent = creds['user_agent'],
        username = creds['user_name'],
        password = creds['password']
    )
    return reddit

def confirm_edit(username, body):
    print(f"This program will edit all posts under the user {username}")
    print(f"The posts will be edited to read:\n{body}")
    response = input('Type YES (uppercase) to edit posts: ')
    if response == 'YES':
        return True
    return False

def confirm_delete(username, subname):
    response = input('ARE YOU SURE?\nType YES (uppercase) to edit posts, or any other key to continue: ')
    if response == 'YES':
        return True
    return False

def get_posts(reddit, username):
    subs = {}
    for post in reddit.redditor(username).comments.new(limit=None):
        if post.subreddit.display_name not in subs:
            subs[post.subreddit.display_name] = [post.id]
        else:
            subs[post.subreddit.display_name].append(post.id)
    return subs
       
def edit_comments(reddit, username, body, subnames):
    for subname, ids in subnames.items():
        if confirm_edit(username, body) == True:
            for post_id in ids:
                reddit.comment(post_id).edit(body)

def delete_comments_by_sub(reddit, username, subnames):
    for subname, ids in subnames.items():
        print(f"posts found in {subname}")
        if confirm_delete(username, subname) == True:
             for post_id in ids:
                 reddit.comment(post_id).delete()
                 print(f"Post {post_id} in {subname} deleted.")
        else:
            print(f"Posts have not been deleted from {subname}")


def main(settings_path):
    creds, settings = parse_config(settings_path)
    print(dope_title)

    reddit = reddit_login(creds)
    body = settings['message']
    username = str(reddit.user.me())
    subnames = get_posts(reddit, username)

    if len(subnames.keys()) > 0:
        for subname, post_id in subnames.items():
            print(f"Post(s) found in the {subname} subreddit.")
            response = input(f"Press 'e' to edit, 'd' to delete or any other key to continue with no changes")
            if response in ('e', 'E'):
                edit_comments(reddit, username, body, subnames)
            elif response in ('d', 'D'):
                delete_comments_by_sub(reddit, username, subnames)
            else:
                print("No posts were modified.")
    else:
        print("No qualifying posts found. Exiting")

   

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('configuration_file', nargs='?')
    args = parser.parse_args()
    settings_path = (args.configuration_file or 'config.ini')
    main(settings_path)
