import React, { Fragment, useContext, useEffect } from 'react';
import { Routes, Route } from 'react-router-dom';
import LandingHome from './components/spa/MainPage';
import NotFound from './components/other/NotFound';
import LandingAdminPage from './components/admin_page/landing_admin_page';
import Dashboard from './components/admin_page/admin_dashboard';
import MemberActions from './components/admin_page/members_page/single_member';
import AddMember from './components/admin_page/members_page/new_member';
import RenderJobs from './components/admin_page/jobs_page/render_jobs';
import JobActions from './components/admin_page/jobs_page/actions_jobs';
import AddJobs from './components/admin_page/jobs_page/add_jobs';
import RenderMentors from './components/admin_page/hackathon/hackathon_mentors/render_mentors';
import AddMentors from './components/admin_page/hackathon/hackathon_mentors/add_mentors';
import MentorsActions from './components/admin_page/hackathon/hackathon_mentors/actions_mentors';
import RenderMembers from './components/admin_page/members_page/render_members';
import RenderJury from './components/admin_page/hackathon/hackathon_jury/render_jury';
import AddJury from './components/admin_page/hackathon/hackathon_jury/add_jury';
import JuryActions from './components/admin_page/hackathon/hackathon_jury/actions_mentors';
import RenderSponsors from './components/admin_page/hackathon/hackathon_sponsors/render_sponsors';
import AddSponsors from './components/admin_page/hackathon/hackathon_sponsors/add_sponsors';
import SponsorsActions from './components/admin_page/hackathon/hackathon_sponsors/actions_sponsors';
import RenderPartners from './components/admin_page/hackathon/hackathon_partners/render_partners';
import AddPartners from './components/admin_page/hackathon/hackathon_partners/add_partners';
import PartnersActions from './components/admin_page/hackathon/hackathon_partners/actions_partners';
import './App.css';
import { HackAUBG } from './components/spa/HackAUBG/HackAUBG';
import { JobsSection } from './components/spa/JobsSection/JobsSection';
import RenderTeams from './components/admin_page/hackathon/hackathon_teams/render_teams';
import RenderTeamMembers from './components/admin_page/hackathon/hackathon_team_members/render_hackathon_team_members';
import TeamActions from './components/admin_page/hackathon/hackathon_teams/actions_teams';

import S3Panel from './components/admin_page/s3_page/s3_landing';
import { RenderStorageObjects } from './components/admin_page/s3_page/render_objects';
import { goBackIfActionsAreStateless, handleUrlDependantStyling } from './Global';
import { FsContext, loadFeatureSwitches, parseFeatureSwitches } from './feature_switches';
import TeamMemberActions from './components/admin_page/hackathon/hackathon_team_members/single_team_member.jsx';
import AddTeamMember from './components/admin_page/hackathon/hackathon_team_members/new_member';
import AddNewTeam from './components/admin_page/hackathon/hackathon_teams/new_team.jsx';
import RenderNoTeamParticipants from './components/admin_page/hackathon/hackathon_no_team_participants/render_no_team_participants';
import NoTeamParticipantsActions from './components/admin_page/hackathon/hackathon_no_team_participants/single_no_team_participant';
import AddNoTeamParticipant from './components/admin_page/hackathon/hackathon_no_team_participants/new_no_team_participant';
import UrlsTable from './components/admin_page/url_shortener/table';
import { Toaster } from 'react-hot-toast';

function App() {
    document.addEventListener('locationChange', handleUrlDependantStyling);
    window.addEventListener('load', handleUrlDependantStyling);
    useEffect(handleUrlDependantStyling, []);

    goBackIfActionsAreStateless();
    // eslint-disable-next-line
    const [featureSwitches, setFeatureSwitches] = useContext(FsContext);

    useEffect(() => {
        const handleFsUpdate = async () => {
            const fs = await loadFeatureSwitches();
            setFeatureSwitches({ ...featureSwitches, ...parseFeatureSwitches(fs) });
        };
        handleFsUpdate();
    }, []);

    return (
        <Fragment>
            <Toaster />
            <Routes>
                <Route path="/" element={<LandingHome />} />
                <Route path="/admin" element={<LandingAdminPage />} />
                <Route path="/admin/dashboard" element={<Dashboard />} />
                <Route path="/admin/dashboard/members" element={<RenderMembers />} />
                <Route path="/admin/dashboard/members/actions" element={<MemberActions />} />
                <Route path="/admin/dashboard/members/add" element={<AddMember />} />
                <Route path="/admin/dashboard/jobs" element={<RenderJobs />} />
                <Route path="/admin/dashboard/jobs/actions" element={<JobActions />} />
                <Route path="/admin/dashboard/mentors" element={<RenderMentors />} />
                <Route path="/admin/dashboard/mentors/add" element={<AddMentors />} />
                <Route path="/admin/dashboard/mentors/actions" element={<MentorsActions />} />
                <Route path="/admin/dashboard/jury" element={<RenderJury />} />
                <Route path="/admin/dashboard/jury/add" element={<AddJury />} />
                <Route path="/admin/dashboard/jury/actions" element={<JuryActions />} />
                <Route path="/admin/dashboard/sponsors" element={<RenderSponsors />} />
                <Route path="/admin/dashboard/sponsors/add" element={<AddSponsors />} />
                <Route path="/admin/dashboard/sponsors/actions" element={<SponsorsActions />} />
                <Route path="/admin/dashboard/partners" element={<RenderPartners />} />
                <Route path="/admin/dashboard/partners/add" element={<AddPartners />} />
                <Route path="/admin/dashboard/partners/actions" element={<PartnersActions />} />
                <Route path="/admin/dashboard/hackathon/teams" element={<RenderTeams />} />
                <Route path="/admin/dashboard/hackathon/teams/members" element={<RenderTeamMembers />} />
                <Route path="/admin/dashboard/hackathon/teams/members/actions" element={<TeamMemberActions />} />
                <Route path="/admin/dashboard/hackathon/teams/members/add" element={<AddTeamMember />} />
                <Route path="/admin/dashboard/hackathon/teams/add" element={<AddNewTeam />} />
                <Route path="/admin/dashboard/hackathon/noteamparticipants/add" element={<AddNoTeamParticipant />} />
                <Route path="/admin/dashboard/hackathon/teams/actions" element={<TeamActions />} />
                <Route path="/admin/dashboard/hackathon/noteamparticipants" element={<RenderNoTeamParticipants />} />
                <Route
                    path="/admin/dashboard/hackathon/noteamparticipants/actions"
                    element={<NoTeamParticipantsActions />}
                />
                <Route path="/admin/dashboard/jobs" element={<RenderJobs />} />
                <Route path="/admin/dashboard/jobs/actions" element={<JobActions />} />
                <Route path="/admin/dashboard/jobs/add" element={<AddJobs />} />

                <Route path="/hackaubg" element={<HackAUBG />} />
                {featureSwitches.jobs ? <Route path="/jobs" element={<JobsSection />} /> : null}
                <Route path="/*" element={<NotFound />} />
                <Route path="/admin/dashboard/s3" element={<S3Panel />} />
                <Route path="/admin/dashboard/s3/objects" element={<RenderStorageObjects />} />
                <Route path="/admin/dashboard/shortener" element={<UrlsTable />} />
            </Routes>
        </Fragment>
    );
}

//vankata oprai neshtata
export default App;
