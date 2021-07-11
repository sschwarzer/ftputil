# ftputil infrastructure migration

## Background

- ftputil is self-hosted on Trac on a VPS (virtual private server) since about
  15 years. Availability of FOSS hosting was relatively limited back then.

- My current VPS provider requires an ancient kernel 2.6.x that doesn't allow
  an upgrade from Debian 9 to Debian 10.

- I could reinstall the services on a new VPS at another provider, but I'd like
  to avoid the work since there's now better FOSS hosting available.


## Current services

- Source hosting (Mercurial server)

- Source browsing (Trac)

- Tickets (Trac)

- Wiki (Trac, hardly used, mostly a few standard pages like documentation and
  downloads)

- Archives for different ftputil versions are attachments of the download page
  in the Trac wiki.

- Mailing list (Mailman)


## Future hosting

### Plan

Move everything to [Sourcehut](https://sourcehut.org/).

### Why not Github (or Gitlab)?

- _Not_ (so much) a reason: Github and Gitlab offer only Git hosting. I'm
  thinking of migrating ftputil to Git (but I'm still not sure). ;-)

- Users pay with their data

- Monoculture, especially with Github

- I find "forks" and "pull requests" weird. Why not send patches?

  https://drewdevault.com/2019/05/24/What-is-a-fork.html


### Sourcehut

- Lightweight site (simple HTML pages, almost no JavaScript)

- Sourcehut is very dedicated to FOSS (TODO: explain this better)

- Paid by users. Users pay for hosting their projects, contributors can
  contribute _without_ paying.

TODO: Give a short summary/explanation of services or link to corresponding
items on Sourcehut.

https://sourcehut.org/blog/2019-10-23-srht-puts-users-first/

## Migration

- The mailing list will probably move to Sourcehut as the first ftputil
  service. I intend to migrate the mailing list archives.

  Users need to register themselves for the new mailing list. I'll send
  information on how to do this.

- Source code hosting will be a repo on Sourcehut. Maybe I'll move to Git
  instead of Mercurial.

  I still think Mercurial is the better system for most users, me included, but
  I dislike switching between VCS tools for work and freetime projects.

- Tickets will be migrated to Sourcehut.

  I tried out different software for the ticket migration already, but I there
  were too many problems. In particular
  [Tracboat](https://github.com/tracboat/tracboat) looked promising at first,
  but I had lots of problems (and tracebacks) and finally gave up.

  Other tools don't allow writing JSON but insist on fetching tickets from Trac
  and uploading the ticket data to Github or Gitlab in one go.

  If you have a recommendation for a tool I should check out, please let me
  know. The tool must be able to convert Trac's wiki format to Github-flavored
  Markdown or another Markdown variant that supports tables with the same
  syntax.

  If all else fails, I consider writing my own migration tool. I don't want to
  lose the tickets.

- I'm not yet sure about the documentation. At least, I'll convert it to
  Markdown, so we can have a link directly into the repo where you can show the
  rendered Markdown. Sourcehut allows this.

- We may not have a dedicated download page in the future. I suppose almost
  everybody installs ftputil from PyPI (Python Package Index).

- Timeline:

  At the latest, the migration must be finished mid-2022 because that's the
  time when support for Debian 9 stops. Currently I'm aiming for finishing the
  migration of all ftputil services by the end of 2021. I don't give any
  guarantees though. :-)
