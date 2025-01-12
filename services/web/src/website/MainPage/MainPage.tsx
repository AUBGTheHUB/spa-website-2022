import { Fragment } from 'react/jsx-runtime';
import IdentitySection from './AboutSection/components/IdentitySection.tsx';
import PastEventSection from './AboutSection/components/PastEventSection.tsx';
import HackAUBGSection from './HackAUBGSection/HackAUBGSection.tsx';

export const MainPage = () => {
    return (
        <Fragment>
            <div className="about-section rounded-2xl py-8">
                <div className="sm:w-3/5 w-11/12 mx-auto">
                    <IdentitySection />
                    <PastEventSection />
                </div>
            </div>
            <HackAUBGSection />
        </Fragment>
    );
};
