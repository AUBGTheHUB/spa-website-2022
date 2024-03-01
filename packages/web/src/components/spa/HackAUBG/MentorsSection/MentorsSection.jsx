import React from 'react';
import axios from 'axios';
import { useState, useEffect } from 'react';
import { url } from '../../../../Global';
import SimpleSlider from '../Carousel';
import styles from './mentors_section.module.css';
export const MentorsSection = () => {
    const [mentor, setMentors] = useState();
    const getMentors = () => {
        axios({
            method: 'get',
            url: url + '/api/mentors',
        })
            .then(res => {
                setMentors(res.data.data.data);
                console.log(res.data.data.data);
            })
            // eslint-disable-next-line
            .catch(err => {
                // do nothing
            });
    };

    const renderMentors = () => {
        if (mentor) {
            return (
                <div className={styles['mentors-section-container']}>
                    <div className={styles['title-container']}>
                        <div className={styles.pac}>
                            <img className={styles['pacman-left']} src="Pacman-left.png"></img>
                        </div>
                        <div className={styles.title}>
                            <h1>Mentors</h1>
                        </div>
                    </div>
                    <div className={styles['mentor-container']}>
                        <SimpleSlider pictures={mentor} view={4}></SimpleSlider>
                    </div>
                </div>
            );
        }
        return (
            <div className={styles['mentors-coming-soon-container']}>
                <h1>
                    Mentors coming <br />
                    soon...
                </h1>
            </div>
        );
    };
    useEffect(() => {
        getMentors();
    }, []);
    return <>{renderMentors()}</>;
};

export default MentorsSection;
