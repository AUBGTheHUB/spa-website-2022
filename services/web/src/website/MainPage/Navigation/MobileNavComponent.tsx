import logo from './images/hublogo.png';
import x from './images/x.svg'; // x icon
import hamburgerMenu from './images/hamburger_menu.svg'; // hamburger menu icon
import { useState } from 'react';
import './navigation.css'; // navigation stylesheet
// this is the navigation bar that is shown if the window size is < 700
// it includes the logo (left-aligned) and a hamburger menu icon
// if showMenu is set to true (by clicking the hamburger icon), the x icon replaces the hamburger menu icon and the dropdown appears

export default function MobileNavComponent() {
    const [showMenu, setShowMenu] = useState(false);
    return (
        <div>
            <div className="navigation">
                <div className="nav-bar flex align-top">
                    <div className="items-left">
                        <img src={logo} className="mobile-logo" />
                    </div>
                    <div className="align-middle items-right">
                        {!showMenu && (
                            <button onClick={() => setShowMenu(!showMenu)}>
                                <img className="icon" src={hamburgerMenu} />
                            </button>
                        )}
                        {showMenu && (
                            <button onClick={() => setShowMenu(!showMenu)}>
                                <img className="icon" src={x} />
                            </button>
                        )}
                    </div>
                </div>
                {showMenu && (
                    <div className="mobile-menu">
                        <p className="mobile-nav-item">
                            <a href="#past-events">Past Events</a>
                        </p>
                        <p className="mobile-nav-item">
                            <a href="#departments">Departments</a>
                        </p>
                        <p className="mobile-nav-item">
                            <a href="#hackathon">Hackathon</a>
                        </p>
                    </div>
                )}
            </div>
            <div className="spacing"></div>
        </div>
    );
}
