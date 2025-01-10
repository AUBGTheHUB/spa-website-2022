import logo from './images/hublogo.png';
import './navigation.css'; // navigation stylesheet
// this is the navigation bar that is shown if the window size is >= 700
// it includes the logo and navigation links

export default function DesktopNavComponent() {
    return (
        <div>
            <div className="navigation">
                <div className="nav-bar flex flex-row align-top">
                    <div className="nav-section-left items-center">
                        <img src={logo} className="desktop-logo" />
                    </div>
                    <div className="nav-section-right flex flex-row items-center">
                        <div className="nav-items">
                            <span className="desktop-nav-item">
                                <a href="#past-events">Past Events</a>
                            </span>
                            <span className="desktop-nav-item">
                                <a href="#departments">Departments</a>
                            </span>
                            <span className="desktop-nav-item">
                                <a href="#hackathon">Hackathon</a>
                            </span>
                        </div>
                    </div>
                </div>
            </div>
            <div className="spacing"></div>
        </div>
    );
}
