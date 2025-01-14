import { useState, useEffect } from 'react';
import DesktopNavComponent from './DesktopNavComponent.tsx';
import MobileNavComponent from './MobileNav.tsx';

const ResponsiveNav = () => {
    const [isDesktop, setIsDesktop] = useState(window.innerWidth >= 700);

    useEffect(() => {
        const handleResize = () => {
            setIsDesktop(window.innerWidth >= 768);
        };

        // Add resize event listener
        window.addEventListener('resize', handleResize);

        // Clean up the event listener on component unmount
        return () => {
            window.removeEventListener('resize', handleResize);
        };
    }, []);

    return <div>{isDesktop ? <DesktopNavComponent /> : <MobileNavComponent />}</div>;
};

export default ResponsiveNav;
