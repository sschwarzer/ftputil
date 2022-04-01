---
permalink: /community
title: Community
---

> Note
>
> When you send information to the mailing list or enter it in the
> ticket system, **make sure all confidential information is removed
> or replaced with dummy data**. This will mostly apply to passwords,
> but depending on your case, such information could also include host
> names of file system paths.
>
> However, keep in mind that changing *too much* information may make
> a problem hard or impossible to reproduce. *For example*, if your
> problem comes from a non-ASCII character in a path, replacing it
> with only ASCII characters in a mail may make the problem impossible
> to reproduce.

## Mailing list

ftputil has a [mailing list]({{ site.data.urls.mailing_list }}).

*For example*, use it to:

- Ask questions
- Discuss improvements
- Get announcements for new versions

If you think you found a bug, it may make sense to discuss the issue
on the mailing list first, in case the issue actually isn't a bug. :-)

The **list address** is\
<mailto:~sschwarzer/ftputil@lists.sr.ht>\
You don't need to subscribe to the list to send a mail.

That said, you can **subscribe** to the list by sending a mail to\
<mailto:~sschwarzer/ftputil+subscribe@lists.sr.ht>\
The list is low-volume, so even if you subscribe, you won't be flooded
with messages. ;-)

You can **unsubscribe** with a mail to\
<mailto:~sschwarzer/ftputil+unsubscribe@lists.sr.ht>

## Ticket system

A tracker for bug reports and enhancement suggestions is at\
<{{ site.data.urls.tracker }}>

You can use [CommonMark markdown](https://commonmark.org/help/) syntax
for the ticket description and comments.

If in doubt whether an issue is a bug, send a mail to the [mailing
list](./#mailing-list) first.

## Source code repository

The source code is hosted in a [Git](https://git-scm.com/) repository
at [Sourcehut]({{ site.data.urls.repository }}).

The license of ftputil is the
[3-clause BSD license](https://opensource.org/licenses/BSD-3-Clause).

## Contributing

*First off*, please do *not* send patches before discussing whether
they're a good fit for ftputil. Send a mail to the [mailing
list](./#mailing-list) first and describe what you'd like to add. I
don't want you to put in the effort to make a patch and then possibly
not having it accepted.

When contributing to ftputil, you have to be sure that you have the
rights to contribute your changes so that they can be distributed
under ftputil's 
[3-clause BSD license](https://opensource.org/licenses/BSD-3-Clause).

[Sourcehut](https://sourcehut.org) doesn't use "pull requests" which
are common with Github or Gitlab. Of course, there are still several
ways to submit patches:

- The [Sourcehut
  documentation](https://man.sr.ht/git.sr.ht/#sending-patches-upstream)
  describes two possible processes. One is the "traditional" way using
  [`git send-email`](https://git-send-email.io/), the other uses a
  web-based tool, [described
  here](https://man.sr.ht/git.sr.ht/#sending-patches-upstream), for
  the patch submission.
- However, since I don't expect a big number of complex contributions,
  I guess we can keep it simple(r) for now: Create and push a branch
  to a public cloned repository of yours and let me know where to find
  it, including the name of the branch. (This is essentially the same
  as you'd do to before actually submitting a pull request on Github.)

  After I know your branch, I can pull from it, play with your code
  and give you feedback.
