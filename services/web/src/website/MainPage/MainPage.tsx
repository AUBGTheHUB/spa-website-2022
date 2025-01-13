import IdentitySection from './AboutSection/components/IdentitySection.tsx';
import PastEventSection from './AboutSection/components/PastEventSection.tsx';
import MeetTheTeam from './AboutSection/components/MeetTheTeam.tsx'

export const MainPage = () => {
    return (
        <div className="about-section rounded-2xl py-8">
            <div className="sm:w-3/5 w-11/12 mx-auto">
                <IdentitySection />
                <PastEventSection />
            </div>
            <div className="mt-40 bg-gradient-to-b from-[#031e4a] to-[#063075] py-10">
                <MeetTheTeam />
            </div>
        </div>
    );
};

