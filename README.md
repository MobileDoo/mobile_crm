# Mobile CRM

![Odoo 18.0](https://img.shields.io/badge/Odoo-18.0-714B67) ![License LGPL-3](https://img.shields.io/badge/license-LGPL--3-blue) ![Version 18.0.1.0.0](https://img.shields.io/badge/version-18.0.1.0.0-informational)

> Opportunities of salespeople in the MobileDoo app: pipeline by stage, notes after a meeting, next step.

Odoo 18 addon of [MobileDoo](https://github.com/MobileDoo) (`mobile_crm`).

## Overview

Sales opportunities in the MobileDoo app: a salesperson works their pipeline by stage, logs a note after a meeting and schedules the
next step in a few taps; team leaders follow their team's pipeline.

## Features

- **My opportunities**, **Follow up** (mine with no next activity or an overdue one) and **Team pipeline** (the teams the user
  leads; every team for sales managers).
- **Stage chips** above the list with counts per stage (won stages last), filtering by stage or by `won`. Only open opportunities
  are listed by default; lost ones are archived by Odoo.
- The real `crm.lead` form with its statusbar, **Won** and **Lost** buttons (including Odoo's lost-reason wizard) and quotation creation.
- Create an opportunity.
- **Log a note and schedule the next activity** from any record (`/form/note`): an internal log note plus an Odoo activity
  (call, meeting, e-mail, to-do) assigned to the caller, idempotent through `client_id`.
- Card fields: expected revenue, probability, stage, priority and the state of the next activity (`overdue`, `today`, `planned`).

## Requirements

| | |
|---|---|
| Odoo | 18.0 (Community or Enterprise) |
| Odoo modules | `crm` |
| MobileDoo addons | [`mobile_connector`](https://github.com/MobileDoo/mobile_connector/tree/18.0) (same branch) |
| Client | the [MobileDoo](https://github.com/MobileDoo) app for Android and iPhone |

This branch targets **Odoo 18** only; use the branch of your Odoo version.

## Installation

```bash
git clone --branch 18.0 https://github.com/MobileDoo/mobile_crm.git
git clone --branch 18.0 https://github.com/MobileDoo/mobile_connector.git
# add the cloned folders to addons_path in odoo.conf, then:
odoo -d <database> -i mobile_crm --stop-after-init
```

The addon is the `mobile_crm/` folder at the root of the repository, so the repository folder itself can go on `addons_path`.

`auto_install` is set: Odoo installs `mobile_crm` by itself as soon as all its dependencies are installed, so putting the folders on `addons_path` and updating the Apps list is enough.

To upgrade after pulling a newer version: `odoo -d <database> -u mobile_crm --stop-after-init`.

## How it works

| Endpoint | Request | Response |
|---|---|---|
| `/records/crm/list` | `{"scope": "mine" | "followup" | "team", "stage_id"?: id | "won", "query"?, "offset"?, "limit"?}` | Cards with `expected_revenue`, `company_currency`, `probability`, `stage_id`, `priority`, `activity_state`, next activity summary |
| `/crm/stages` | `{"scope"}` | `{"stages": [{id, name, count, is_won}], "open", "won"}` for the chips |
| `/form/note` (core) | `{"model", "id", "body"?, "activity"?: {type, date, summary?}, "client_id"?}` | `{message_id, activity_id}` |

### Capabilities

| Capability | Granted when |
|---|---|
| `view` | member of `sales_team.group_sale_salesman` and may read `crm.lead` |
| `create` | as `view`, and may create `crm.lead` |
| `team` | team leader, sales manager, or member of the *see all leads* group |

The home tiles `crm_mine`, `crm_followup` and `crm_team` and the tab *Opportunities* follow these capabilities.

## Security

No groups, ACLs or data are added. The signed-in user's CRM access rights and record rules decide what is listed or changed; note
and activity creation requires write access to the record, as on the web.

## Extending

Change scopes with `_mobile_domain(scope, params)` or the base domain `_base_domain`, the stage chips with `_mobile_stages`, and defaults
of a new opportunity with `_mobile_new_context()` on `mobile.crm.service`. Extra fields come from *Mobile App > Extra Fields*.

## Contributing

Issues and pull requests are welcome. Open pull requests against the branch of the Odoo version you are fixing (this one is `18.0`) and
keep the change inside the `mobile_crm/` folder.

These repositories are published from MobileDoo's development repository, which remains the source of truth. A merged pull request is
taken back there, and the branches of the other Odoo versions are updated by the maintainers, so a fix is usually welcome even if you can
only test it on one version. `README.md` and `LICENSE` are generated at each release; changes to them are not carried back.

## License

LGPL-3: see [LICENSE](LICENSE).
