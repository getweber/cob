# Cob


![Build Status] (https://secure.travis-ci.org/getweber/cob.png )

Cob is a tool for building ambitious webapps using Python. It is greatly inspired by Ember's [ember-cli](https://ember-cli.com/).

Cob projects are structured repositories, containing multiple *modules* of different *types*. Modules add functionality to your project, and declare the basic settings needed to get them operational. Not to be confused with Python modules, Cob modules can add all sorts of functionality -- static files, frontend frameworks, DB migrations and more.

# Getting Started

## Installation

```
$ pip install cob
```

## Generating your Project

```
$ cob generate project myproj
```

This will create a new directory called `myproj` with the minimal skeleton you need to get going.

## Your First Module - Blueprints

The most basic kind of module we can add to our project is *blueprints*, which are actually Flask blueprints. Let's add a blueprint that greets the user, and will sit under the `/hello` URL path:

```
$ cd myproj
$ cob generate blueprint greeter /hello
```

This creates a subdirectory inside our project with a YAML file inside, `.cob.yml` (which is how a Cob module is defined):

```
$ cd greeter
$ cat .cob.yml
type: blueprint
blueprint: blueprint:blueprint
mountpoint: /hello
```

This tells Cob to load this module as a blueprint, and register it under `/hello`.

We can modify `greeter/blueprint.py` to fit our needs:

```python
# greeter/blueprint.py
...

@blueprint.route('/')
def say_hi():
    return 'hi'
```

Now we can run our test server and see that it works:

```
# in the project root
$ cob testserver
...
```

```
$ curl http://127.0.0.1:5000/hello/
hi
```



# Licence

BSD3

