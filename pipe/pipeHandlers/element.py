#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import shutil
from pipe.pipeHandlers.environment import Environment
from pipe.pipeHandlers import pipeline_io

'''
This Checkout class is not used in the Cenote pipeline, it's
just included because it was part of the old DCC Pipe.

Rather, the functionality of checking-in or checking-out
a shot was included as part of the Element class.
'''
class Checkout:
    """
    class describing the result of an element checkout
    """
    PIPELINE_FILENAME = ".checkout"

    USER = "user"
    BODY = "body_name"
    ELEMENT = "element_name"
    FILES = "filename"
    TIMES = "time"

    @staticmethod
    def create_new_dict(username, body, department, element):
        """
        populate a dictionary with defaults for all the fields needed to create a new checkout
        """
        datadict = {}
        datadict[Checkout.USER] = username
        datadict[Checkout.BODY] = body
        datadict[Checkout.ELEMENT] = element
        datadict[Checkout.FILES] = []
        datadict[Checkout.TIMES] = []
        return datadict

    def __init__(self, filepath):
        """
        create a checkout instance describing the result of the checkout operation in the given filepath
        if it is not a valid checkout directory, raise EnvironmentError
        """
        self._filepath = filepath
        self._pipeline_file = os.path.join(filepath, self.PIPELINE_FILENAME)
        if not os.path.exists(self._pipeline_file):
            raise EnvironmentError("not a valid checkout directory: " + self._filepath)
        self._datadict = pipeline_io.readfile(self._pipeline_file)

    def get_body_name(self):

        return self._datadict[self.BODY]

    def get_department_name(self):

        return self._datadict[self.DEPARTMENT]

    def get_element_name(self):

        return self._datadict[self.ELEMENT]

    def get_user_name(self):

        return self._datadict[self.USER]

    def list_files(self):
        """
        list all the files that have been created in this checkout directory from valid checkout operations
        """
        return self._datadict[self.FILES]

    def list_times(self):
        """
        list all the timestamps of checkout operations performed in this checkout directory
        """
        return self._datadict[self.TIMES]

    def add_operation(self, filepath):
        """
        record the result of a checkout operation.
        filepath -- the file that was checked out as a result of the operation.
        """
        self._datadict[self.FILES].append(filepath)
        self._datadict[self.TIMES].append(pipeline_io.timestamp())
        pipeline_io.writefile(self._pipeline_file, self._datadict)


class Element:
    """
    Abstract class describing elements that make up an asset or shot body.
    """
    PIPELINE_FILENAME = ".element"
    DEFAULT_NAME = "main"
    DEFAULT_CACHE_DIR = "cache"
    DEFAULT_RENDER_DIR = "render"

    NAME = "name"
    PARENT = "parent"
    LATEST_VERSION = "latest_version"
    PUBLISHES = "publishes"
    CHECKOUT_USERS = "checkout_users"
    APP_EXT = "app_ext"
    CACHE_EXT = "cache_ext"
    CACHE_FILEPATH = "cache_filepath"
    ASSIGNED_USER = "assigned_user"

    def __init__(self, filepath=None):
        """
        create an element instance describing the element stored in the given filepath.
        if none given, creates an empty instance.
        """
        self._env = Environment()
        self.app_ext = None

        if filepath is not None:
            self.load_pipeline_file(filepath)
            cache_dir = self.get_cache_dir()
            if not os.path.exists(cache_dir):
                pipeline_io.mkdir(cache_dir)
        else:
            self._filepath = None
            self._pipeline_file = None
            self._datadict = None

    def create_new_dict(self, name, department, parent_name):
        """
        populate a dictionary with defaults for all the fields needed to create a new element
        """
        datadict = {}
        datadict[Element.NAME] = name
        datadict[Element.PARENT] = parent_name
        datadict[Element.LATEST_VERSION] = -1
        datadict[Element.PUBLISHES] = []
        datadict[Element.CHECKOUT_USERS] = []
        datadict[Element.APP_EXT] = self.app_ext
        datadict[Element.CACHE_EXT] = ""
        datadict[Element.CACHE_FILEPATH] = ""
        datadict[Element.ASSIGNED_USER] = ""
        return datadict

    def update_app_ext(self, extension):
        self._datadict[Element.APP_EXT] = extension
        self._update_pipeline_file()

    def load_pipeline_file(self, filepath):
        """
        load the pipeline file that describes this element
        """
        self._filepath = filepath
        self._pipeline_file = os.path.join(filepath, self.PIPELINE_FILENAME)
        if not os.path.exists(self._pipeline_file):
            raise EnvironmentError("not a valid element: " + self._pipeline_file + " does not exist")
        self._datadict = pipeline_io.readfile(self._pipeline_file)

    def _update_pipeline_file(self):

        pipeline_io.writefile(self._pipeline_file, self._datadict)

    def get_name(self):

        return self._datadict[self.NAME]

    def get_parent(self):

        return self._datadict[self.PARENT]

    def get_dir(self):
        """
        return the directory all data for this element is stored in
        """
        return self._filepath

    def get_department(self):

        return self._datadict[self.DEPARTMENT]

    def get_long_name(self):
        """
        return a string describing a unique name for this asset:
        {the parent body's name}_{this element's department}_{this element's name}
        """
        return self.get_parent()+"_"+self.get_department()+"_"+self.get_name()

    def get_short_name(self):
        """
        return a string describing a the name for this asset:
        {the parent body's name}_{this element's name}
        in this version the department is not included
        consider it the name for all parts of the asset
        """
        return self.get_parent()+"_"+self.get_name()

    def get_assigned_user(self):
        """
        returns the username (string) of the assigned user
        """
        if not self._datadict.has_key(self.ASSIGNED_USER):
            self._datadict[self.ASSIGNED_USER] = ""
            self._update_pipeline_file()

        return self._datadict[self.ASSIGNED_USER]

    def get_last_version(self):
        """
        returns latest version number
        """
        return self._datadict[self.LATEST_VERSION]

    def get_last_publish(self):
        """
        return a tuple describing the latest publish: (username, timestamp, comment, filepath)
        """
        latest_version = self._datadict[self.LATEST_VERSION]
        if(latest_version<0):
            return None
        return self._datadict[self.PUBLISHES][latest_version]

    def list_publishes(self):
        """
        return a list of tuples describing all publishes for this element.
        each tuple contains the following: (username, timestamp, comment, filepath)
        """
        return self._datadict[self.PUBLISHES]

    def get_last_note(self):
        """
        return the latest note created for this element as a string
        """
        if(len(self._datadict[self.NOTES])>0):
            return self._datadict[self.NOTES][-1]
        else:
            return ""
    def list_notes(self):
        """
        return a list of all notes that have beeen created for this element
        """
        return self._datadict[self.NOTES]

    def get_start_date(self):

        return self._datadict[self.START_DATE]

    def get_end_date(self):

        return self._datadict[self.END_DATE]

    def get_app_ext(self):
        """
        return the extension of the application files for this element (including the period)
        e.g. the result for an element that uses maya would return ".mb"
        """
        return self._datadict[self.APP_EXT]

    def get_app_filename(self):
        """
        return the name of the application file for this element. This is just the basename
        of the file, not the absolute filepath.
        """
        return str(self.get_long_name())+str(self.get_app_ext())

    def get_app_filepath(self):
        """
        return the absolute filepath of the application file for this element
        """
        filename = self.get_app_filename()
        return os.path.join(self._filepath, filename)

    def get_version_dir(self, version):
        """
        return the path to the directory of the given version
        """
        return os.path.join(self._filepath, ".v%04d" % version)

    def get_cache_ext(self):
        """
        return the extension of the cache files for this element (including the period)
        e.g. the result for an element that uses alembic caches would return ".abc"
        """
        return self._datadict[self.CACHE_EXT]

    def get_cache_dir(self): 

        return os.path.join(self._filepath, self.DEFAULT_CACHE_DIR)

    def get_render_dir(self):

        render_dir = os.path.join(self._filepath, self.DEFAULT_RENDER_DIR)
        if not os.path.exists(render_dir):
            pipeline_io.mkdir(render_dir)
        return render_dir

    def list_checkout_users(self):
        """
        return a list of the usernames of all users who have checked out this element
        """
        return self._datadict[self.CHECKOUT_USER]

    def is_assigned(self):
        """
        return whether or not there's an assigned user
        """
        if not self._datadict.has_key(self.ASSIGNED_USER):
            self._datadict[self.ASSIGNED_USER] = ""
            self._update_pipeline_file()
            return False
            
        user = self._datadict[self.ASSIGNED_USER]
        if user == "":
            return False
        else:
            return True

    def update_assigned_user(self, username):
        """
        Update the user assigned to this element.
        username -- the username (string) of the new user to be assigned
        """
        if not self._datadict.has_key(self.ASSIGNED_USER):
            self._datadict[self.ASSIGNED_USER] = username
            self._update_pipeline_file()
            return
        old_username = self._datadict[self.ASSIGNED_USER]
        if(old_username==username):
            return
        self._datadict[self.ASSIGNED_USER] = username
        self._update_pipeline_file()

    def update_start_date(self, date):
        """
        Update the start date of this element.
        date -- the new start date
        """
        self._datadict[self.START_DATE] = date
        self._update_pipeline_file()

    def update_end_date(self, date):
        """
        Update the end date of this element.
        date -- the new end date
        """
        self._datadict[self.END_DATE] = date
        self._update_pipeline_file()

    def update_checkout_users(self, username):
        """
        add the given username to the checkout_users list, if they aren't already in it.
        """
        if username not in self._datadict[self.CHECKOUT_USERS]:
            self._datadict[self.CHECKOUT_USERS].append(username)
            self._update_pipeline_file()

    def update_notes(self, note):
        """
        add the given note to the note list
        """
        self._datadict[self.NOTES].append(note)
        self._update_pipeline_file()

    def get_checkout_dir(self, username):
        """
        return the directory this element would be copied to during checkout for the given username
        """
        return os.path.join(self._env.get_users_dir(), username, self.get_long_name())

    def checkout(self, username):
        """
        Copies the element to the given user's work area in a directory with the following name:
            {the parent body's name}_{this element's department}_{this element's name}
        Adds username to the list of checkout users.
        username -- the username (string) of the user performing this action
        Returns the absolute filepath to the copied file. If this element has no app file,
        the returned filepath will not exist.
        """
        checkout_dir = self.get_checkout_dir(username)
        if not os.path.exists(checkout_dir):
            pipeline_io.mkdir(checkout_dir)
            datadict = Checkout.create_new_dict(username, self.get_parent(), self.get_department(), self.get_name())
            pipeline_io.writefile(os.path.join(checkout_dir, Checkout.PIPELINE_FILENAME), datadict)
        checkout = Checkout(checkout_dir)
        app_file = self.get_app_filepath()
        checkout_file = pipeline_io.version_file(os.path.join(checkout_dir, self.get_app_filename()))
        if os.path.exists(app_file):
            shutil.copyfile(app_file, checkout_file)
            checkout.add_operation(checkout_file)
        self.update_checkout_users(username)
        return checkout_file

    def publish(self, username, path, comment, asset_name):
        """
        Update the version number and save publish information in the
        element file. Save the file at path in a version
        folder as well as in the main element folder. If the given path
        isn't the same as the version folder or main element folder, the
        file at path will be deleted.

        username -- the username of the user performing this action
        path -- a string representing the path to the published file
        comment -- description of changes made in this publish
        asset_name -- name of the asset being published
        """
        #get the new version number
        new_version = self._datadict[self.LATEST_VERSION] + 1
        self._datadict[self.LATEST_VERSION] = new_version

        #path to the file that will be saved in the same folder as the .element file
        main_path = asset_name + "_" + self.get_name() + self.get_app_ext()
        main_path = os.path.join(self._filepath, main_path)
        print(main_path)

        #path to the file that will be saved in the version folder
        version_path = self.get_version_dir(new_version)
        pipeline_io.mkdir(version_path)
        version_path = os.path.join(version_path, asset_name + self.get_app_ext())
        print(version_path)

        if path != main_path and path != version_path:
            #copy the file then delete the original
            shutil.copyfile(path, main_path)
            shutil.copyfile(path, version_path)

            pipeline_io.set_permissions(main_path)
            pipeline_io.set_permissions(version_path)

            os.remove(path)

        elif path == main_path:
            shutil.copyfile(path, version_path)
            pipeline_io.set_permissions(version_path)

        elif path == version_path:
            shutil.copyfile(path, main_path)
            pipeline_io.set_permissions(main_path)

        #save publish data to the .element file
        timestamp = pipeline_io.timestamp()
        self._datadict[self.PUBLISHES].append((username, timestamp, comment, main_path))
        self._update_pipeline_file()


    def update_cache(self, src, reference=False):
        """
        Update the cache of this element.
        src -- the new cache file
        reference -- if false (the default) copy the source into this element's cache folder.
                     if true create a symbolic link to the given source.
                     the reference is useful for very large cache files, where copying would be a hassle.
        """
        if not os.path.exists(src):
            raise EnvironmentError("file does not exist: "+src)
        cache_filename = os.path.basename(src)
        cache_dir = self.get_cache_dir()
        cache_filepath = os.path.join(cache_dir, cache_filename)
        if not os.path.exists(cache_dir):
            pipeline_io.mkdir(cache_dir)

        if reference: # TODO: sequences?
            ref_path = os.path.normpath(src)
            if not ref_path.startswith(self._env.get_project_dir()):
                raise EnvironmentError("attempted reference is not in the project directory: "+ref_path)
            self._datadict[self.CACHE_FILEPATH] = ref_path
            os.symlink(ref_path, cache_filepath)
        else:
            self._datadict[self.CACHE_FILEPATH] = cache_filepath
            if os.path.isdir(src):
                shutil.copytree(src, cache_filepath)
            else:
                shutil.copyfile(src, cache_filepath)

        self._update_pipeline_file()

    def list_cache_files(self):
        """
        list all cache files that have been published to this element.
        """
        cache_list = os.listdir(self.get_cache_dir())
        return cache_list
