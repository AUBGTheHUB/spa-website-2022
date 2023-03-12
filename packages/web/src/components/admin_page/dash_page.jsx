import React from 'react';
import { Card, Button } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';
import InvalidClient from './invalid_client';
import Validate from '../../Global';
const Dash = () => {
    const history = useNavigate();

    console.log('Dashboard!');

    if (Validate()) {
        return (
            <div className="dash">
                <div className="dash-box">
                    <Card className="card-dash-landing">
                        <Card.Body>
                            <Card.Title>Members</Card.Title>
                            <Card.Text>
                                Add, edit or remove members of the club.
                            </Card.Text>
                            <Button
                                variant="primary"
                                onClick={() => {
                                    history('/admin/dashboard/members', {
                                        state: {}
                                    });
                                }}
                            >
                                See current members
                            </Button>
                        </Card.Body>
                    </Card>
                    <Card className="card-dash-landing">
                        <Card.Body>
                            <Card.Title>Events</Card.Title>
                            <Card.Text>
                                Add, edit or remove old and upcoming events.
                            </Card.Text>
                            <Button
                                variant="primary"
                                onClick={() => {
                                    history('/admin/dashboard/events');
                                }}
                            >
                                See current events
                            </Button>
                        </Card.Body>
                    </Card>
                    <Card className="card-dash-landing">
                        <Card.Body>
                            <Card.Title>Articles</Card.Title>
                            <Card.Text>
                                Upload articles written by members of the club.{' '}
                            </Card.Text>
                            <Button
                                variant="primary"
                                onClick={() =>
                                    history('/admin/dashboard/articles')
                                }
                            >
                                See current articles
                            </Button>
                        </Card.Body>
                    </Card>
                    <Card className="card-dash-landing">
                        <Card.Body>
                            <Card.Title>Jobs</Card.Title>
                            <Card.Text>
                                Add or remove job positions provided by our
                                sponsors.
                            </Card.Text>
                            <Button
                                variant="primary"
                                onClick={() => {
                                    history('/admin/dashboard/jobs', {
                                        state: {}
                                    });
                                }}
                            >
                                See current job positions
                            </Button>
                        </Card.Body>
                    </Card>
                    <Card className="card-dash-landing">
                        <Card.Body>
                            <Card.Title>Hackathon Mentors</Card.Title>
                            <Card.Text>
                                Add or remove hackathon mentors.
                            </Card.Text>
                            <Button
                                variant="primary"
                                onClick={() => {
                                    history('/admin/dashboard/mentors');
                                }}
                            >
                                See hackathon mentors
                            </Button>
                        </Card.Body>
                    </Card>
                    <Card className="card-dash-landing">
                        <Card.Body>
                            <Card.Title>Hackathon Jury</Card.Title>
                            <Card.Text>
                                Add or remove current hackathon jury.
                            </Card.Text>
                            <Button
                                variant="primary"
                                onClick={() => {
                                    history('/admin/dashboard/jury');
                                }}
                            >
                                See current hackathon jury
                            </Button>
                        </Card.Body>
                    </Card>
                    <Card className="card-dash-landing">
                        <Card.Body>
                            <Card.Title>Hackathon Sponsors</Card.Title>
                            <Card.Text>
                                Add or remove hackathon sponsors.
                            </Card.Text>
                            <Button
                                variant="primary"
                                onClick={() => {
                                    history('/admin/dashboard/sponsors');
                                }}
                            >
                                See current sponsors
                            </Button>
                        </Card.Body>
                    </Card>
                    <Card className="card-dash-landing">
                        <Card.Body>
                            <Card.Title>Hackathon Partners</Card.Title>
                            <Card.Text>
                                Add or remove hackathon partners.
                            </Card.Text>
                            <Button
                                variant="primary"
                                onClick={() => {
                                    history('/admin/dashboard/partners');
                                }}
                            >
                                See current partners
                            </Button>
                        </Card.Body>
                    </Card>
                    <Card className="card-dash-landing">
                        <Card.Body>
<<<<<<< HEAD
                            <Card.Title>Hackathon Teams</Card.Title>
                            <Card.Text>Edit hackathon teams.</Card.Text>
=======
                            <Card.Title>Hackathon teams</Card.Title>
                            <Card.Text>
                                Manage the hackathon teams
                            </Card.Text>
>>>>>>> d06cb3e (#310 Fix hackathon teams display and adding functionalities)
                            <Button
                                variant="primary"
                                onClick={() => {
                                    history('/admin/dashboard/hackathon/teams');
                                }}
                            >
<<<<<<< HEAD
                                See current teams
=======
                                Manage
>>>>>>> d06cb3e (#310 Fix hackathon teams display and adding functionalities)
                            </Button>
                        </Card.Body>
                    </Card>
                    <Card className="card-dash-landing">
                        <Card.Body>
                            <Card.Title>Image Management</Card.Title>
                            <Card.Text>
                                Management window for S3 objects
                            </Card.Text>
                            <Button
                                variant="primary"
                                onClick={() => {
                                    history('/admin/dashboard/s3');
                                }}
                            >
                                Manage
                            </Button>
                        </Card.Body>
                    </Card>
                </div>
            </div>
        );
    } else {
        return <InvalidClient />;
    }
};

export default Dash;
