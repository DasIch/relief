Contributing
============

Contributions in any form are always welcome. If you think you have found a bug,
you have an idea you think might improve things or even better you already have
code and can make a pull request, do not hesistate to create an issue or make
that pull request.

Nevertheless there are a couple of things to be aware of:

1. Be nice. We have a :ref:`code-of-conduct`, please read and follow it.
2. If you have found a bug or have an idea on how to improve things, chances
   are someone else did as well; so please run a search on the issue tracker
   if someone else had the same idea already, contribute to the discussion if
   that makes sense, if you are the first create an issue.
3. If you are contributing code, try to be consistent with the code you are
   modifying, if in doubt follow :pep:`8`.
4. If you are thinking of contributing a lot of code or making big changes, get
   in contact before writing it. The more code you write and the more changes
   you do, the bigger the chance of disagreement and it is very disappointing
   for everyone if the code will not be merged. Let us prevent this early
   through communication.


Setting up a development environment
------------------------------------

Setting up a development environment to work on Relief is fairly trivial.
Nevertheless this is how you get started:

The first step is forking the repository_ on GitHub. Once you have done that
you can clone your fork to create a local repository using::

   $ git clone git@github.com:YourGitHubName/relief.git

Having done that you should probably create a virtual environment using
virtualenv_ and activate it. If you don't know what virtualenv is, you should
learn about it before continuing, it is a very useful tool that you should be
familiar with if you are doing anything serious in Python.

So once you have created your virtual environment and activated it, it is time
to install all development tools and relief dependencies. You can do that by
running::

   $ make dev

This may take a while, once it is done you should have setup the development
environment successfully. You can test that everything works by running::

   $ make test


This will run all tests, all of which should pass.

You have no idea what to do now? Take a look at the `open issues`_ may be you
will find an interesting challenge there.

.. _repository: https://github.com/DasIch/relief
.. _virtualenv: http://www.virtualenv.org/en/latest/
.. _open issues: https://github.com/DasIch/relief/issues?state=open


Running tests
-------------

We use pytest_ for testing, you can execute the tests with it using::

   $ py.test

To test code and documentation on all supprted interpreters, we use tox_,
which is invoked like this::

   $ tox

.. _pytest: http://pytest.org/latest/
.. _tox: http://testrun.org/tox/latest/


.. _code-of-conduct:

Code of Conduct
---------------

Like the technical community as a whole, the Relief team and community is made
up of a mixture of professionals and volunteers from all over the world,
working on every aspect of the missing - including mentorship, teaching and
connecting people.

Diversity is one of our huge strengths, but it can also lead to communication
issues and unhappiness. To that end, we have a few ground rules that we ask
people to adhere to when they're participating within this community and
project. These rules apply equally to contributors and those seeking help.

This isn't an exhaustive list of things you can't do. Rather, take it in the
spirit in which it's intended - a guide to make it easier to enrich all of us
and the technical communities in which we participate.

This code of conduct applies to all communication.

* Be welcoming, friendly, and patient.
* Be considerate. Your work will be used by other people, and you in turn
  will depend on the work of others. Any decision you take will affect users
  and colleagues, and you should take those consequences into account when
  making decisions.
* Be respectful. Not all of us will agree all the time, but disagreement is
  no excuse for poor behaviour and poor manners. We might all experience some
  frustration now and then, but we cannot allow that frustration to turn into
  a personal attack. It's important to remember that a community where people
  feel uncomfortable or threatened is not a productive one. Members of the
  Relief community should be respectful when dealing with other members as
  well as with people outside the Relief community.
* Be careful in the words that you choose. Remember that sexist, racist, and
  other exclusionary jokes can be offensive to those around you. Be kind to
  others. Do not insult or put down other participants. Behave professionally.
  Remember that harassment and sexist, racist, or exclusionary jokes are not
  appropriate for the community.

When we disagree, we try to understand why. Disagreements, both social and
technical, happen all the time and Relief is no exception. It is important
that we resolve disagreements and differing views constructively. Remember
that we're different. The strength of Relief comes from its varied community,
people from a wide range of backgrounds. Different people have different
perspective on issues. Being unable to understand why someone holds a
viewpoint doesn't mean that they're wrong. Don't forget that is is human to
err and blaming each other doesn't get us anywhere, rather offer to help
resolving issues and to help learn from mistakes.

This text is a slightly modified version of the `Speak Up! Code of Conduct`_
which is available under a `CC BY 3.0`_ license and was inspired by the
`Fedora Project`_ and the `Python Mentorship Project`_.


.. _Speak Up! Code of Conduct: http://speakup.io/coc.html
.. _CC BY 3.0: http://creativecommons.org/licenses/by/3.0
.. _Fedora Project: http://fedoraproject.org/code-of-conduct
.. _Python Mentorship Project: http://pythonmentors.com
