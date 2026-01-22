from model.site_state import SiteState


def build_site_states(subject_states):
    sites = {}

    for subject in subject_states.values():
        site_id = subject.site_id

        if site_id not in sites:
            sites[site_id] = SiteState(
                site_id=site_id,
                region=subject.region
            )

        sites[site_id].subjects.append(subject)

    for site in sites.values():
        site.compute()

    return sites
