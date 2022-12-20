import { Button } from './Button';
import React from 'react';
import './mobile_navbar.css';
import { CgMenu } from 'react-icons/cg';
import { MdOutlineClose } from 'react-icons/md';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export const NavMobile = () => {
    const navigate = useNavigate();

    const navigateToHackAUBG = () => {
        navigate('/hackaubg');
    };

    const [menuClass, setMenuClass] = useState('navmobile-menu not-displayed');
    const [closeButton, setCloseButton] = useState(
        'navmobile-button-close not-displayed'
    );

    const closeMenu = () => {
        setMenuClass('navmobile-menu-backwards');
    };

    return (
        <div className="navmobile-body">
            <div className="navmobile-container">
                <img src="hublogo.png" className="navmobile-logo"></img>
                <h2 className="navmobile-title">The Hub</h2>
                <Button
                    props={{
                        css: 'navmobile-button',
                        icon: (
                            <CgMenu
                                className="navmobile-button icon"
                                onClick={() => {
                                    setMenuClass('navmobile-menu forwards');
                                    setCloseButton('navmobile-button-close');
                                }}
                            />
                        )
                    }}
                />
            </div>

            <div className={menuClass}>
                <Button
                    props={{
                        css: 'navmobile-button-close',
                        icon: (
                            <MdOutlineClose
                                className={closeButton}
                                onClick={() => {
                                    setMenuClass('navmobile-menu-backwards');
                                }}
                            />
                        )
                    }}
                />

                {/* Anchors are clickable / selectable */}

                <div className="navmobile-anchors-container">
                    <ul>
                        <li>
                            <a href="#about" onClick={closeMenu}>
                                About
                            </a>
                        </li>
                        <li>
                            <a href="#events" onClick={closeMenu}>
                                Events
                            </a>
                        </li>
                        <li>
                            <a href="#articles" onClick={closeMenu}>
                                Articles
                            </a>
                        </li>
                        <li>
                            <a href="#team" onClick={closeMenu}>
                                Team
                            </a>
                        </li>
                        <li>
                            <a href="#jobs" onClick={closeMenu}>
                                Jobs
                            </a>
                        </li>
                        <div>
                            <div
                                className="navmobile-button-ham"
                                onClick={navigateToHackAUBG}
                            >
                                HackAUBG
                            </div>
                        </div>
                    </ul>
                </div>
            </div>
        </div>
    );
};
