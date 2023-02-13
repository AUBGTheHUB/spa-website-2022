import React from 'react';
import { openNewTab } from '../../../../Global';

export const MentorsCard = ({ Mentor }) => {
    return (
        <div className="mentor-card">
            <div className="mentor-image">
                <img src={Mentor.profilepicture} onClick={openNewTab} />
            </div>
            <div className="mentor-link">
                <a href={Mentor.sociallink}></a>
            </div>
        </div>
    );
};
