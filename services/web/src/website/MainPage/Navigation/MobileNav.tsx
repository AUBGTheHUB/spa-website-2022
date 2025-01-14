import logo from './images/hublogo.png';
import hamburgerMenuIcon from './images/hamburger_menu.svg';
import photoIcon from './images/past_events.svg';
import threeDots from './images/departments.svg';
import codeIcon from './images/hackathon.svg';
import './navigation.css'; // navigation stylesheet
import { Sheet, SheetContent, SheetHeader, SheetTrigger } from '@/components/ui/sheet';
// this is the navigation bar that is shown if the window size is < 700
// it includes the logo (left-aligned) and a hamburger menu icon

export default function MobileNavComponent() {
    return (
        <div>
            <div className="navigation">
                <div className="nav-bar flex align-top">
                    <div className="items-left">
                        <img src={logo} className="mobile-logo" />
                    </div>
                </div>
                <Sheet>
                    <SheetTrigger>
                        <img className="icon" src={hamburgerMenuIcon} />
                    </SheetTrigger>
                    <SheetContent>
                        <SheetHeader></SheetHeader>
                        <br />
                        <div className="mobile-nav-item">
                            <img src={photoIcon} />
                            <a href="#past-events">Past Events</a>
                        </div>
                        <br />
                        <div className="mobile-nav-item">
                            <img src={threeDots} />
                            <a href="#departments">Departments</a>
                        </div>
                        <br />
                        <div className="mobile-nav-item">
                            <img src={codeIcon} />
                            <a href="#hackathon">Hackathon</a>
                        </div>
                    </SheetContent>
                </Sheet>
            </div>
            <div className="spacing"></div>
        </div>
    );
}
