const API = 'http://result-day-alb-696181440.ap-south-1.elb.amazonaws.com';

let PRN = sessionStorage.getItem('resultday_prn') || '';
let student = {};
let results = [];
let subjects = [];
let exams = [];
let notifications = [];

const $ = s => document.querySelector(s);

const esc = v =>
    String(v ?? '').replace(/[&<>"']/g, c => ({
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    }[c]));

const pick = (obj, keys, fallback = '—') => {
    for (const key of keys) {
        if (
            obj &&
            obj[key] !== undefined &&
            obj[key] !== null &&
            obj[key] !== ''
        ) {
            return obj[key];
        }
    }
    return fallback;
};

const num = v =>
    Number.isFinite(Number(v)) ? Number(v) : null;

const fmt = v =>
    num(v) === null ? '—' : num(v).toFixed(2);

const arr = (x, key) =>
    Array.isArray(x)
        ? x
        : Array.isArray(x?.[key])
            ? x[key]
            : [];


/* =========================================================
   API
========================================================= */

async function api(path, opt = {}) {
    const response = await fetch(API + path, {
        ...opt,
        headers: {
            'Content-Type': 'application/json',
            ...(opt.headers || {})
        }
    });

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
        throw Error(
            pick(
                data,
                ['message', 'error'],
                `Request failed ${response.status}`
            )
        );
    }

    return data;
}


/* =========================================================
   STUDENT IDENTITY
========================================================= */

function identity(s) {
    student = s || {};

    const name = pick(
        student,
        ['name', 'student_name', 'studentName'],
        'Student'
    );

    const prn = pick(
        student,
        ['PRN', 'prn'],
        PRN
    );

    const initials = name
        .split(/\s+/)
        .slice(0, 2)
        .map(x => x[0])
        .join('')
        .toUpperCase();

    [
        'sideAvatar',
        'topAvatar',
        'dashAvatar',
        'profileAvatar'
    ].forEach(id => {
        const el = $('#' + id);
        if (el) el.textContent = initials;
    });

    if ($('#sideName'))
        $('#sideName').textContent = name;

    if ($('#sidePrn'))
        $('#sidePrn').textContent = prn;

    if ($('#topName'))
        $('#topName').textContent = name;

    if ($('#dashName'))
        $('#dashName').textContent = name.split(' ')[0];

    if ($('#dashStudent'))
        $('#dashStudent').textContent = name;

    if ($('#dashBranch'))
        $('#dashBranch').textContent =
            pick(student, ['branch']);

    if ($('#profileName'))
        $('#profileName').textContent = name;

    if ($('#profilePrn'))
        $('#profilePrn').textContent = prn;
}


/* =========================================================
   HELPERS
========================================================= */

function currentSemester() {
    return (
        num(
            pick(
                student,
                [
                    'current_semester',
                    'currentSemester',
                    'semester'
                ],
                0
            )
        ) || 0
    );
}


function latestPublishedResult() {
    const published = results.filter(
        r =>
            String(r.status || '').toUpperCase() !== 'SCHEDULED'
    );

    return published.length
        ? published[published.length - 1]
        : null;
}


/* =========================================================
   LOAD ALL DATA
========================================================= */

async function load() {
    try {
        const [
            dashboardData,
            resultsData,
            subjectsData,
            examsData,
            notificationsData
        ] = await Promise.all([
            api(`/dashboard/${PRN}`),
            api(`/results/${PRN}`),
            api(`/subjects/${PRN}`),
            api(`/exams/${PRN}`),
            api(`/notifications/${PRN}`)
        ]);

        identity(
            dashboardData.student ||
            dashboardData.data ||
            dashboardData
        );

        results = arr(
            resultsData,
            'results'
        ).sort(
            (a, b) =>
                num(a.semester) - num(b.semester)
        );

        subjects = arr(
            subjectsData,
            'subjects'
        );

        exams = arr(
            examsData,
            'exams'
        );

        notifications = arr(
            notificationsData,
            'notifications'
        );

        render();

    } catch (error) {

        if ($('#error')) {
            $('#error').textContent = error.message;
            $('#error').classList.remove('hidden');
        }

        render();
    }
}


/* =========================================================
   MAIN RENDER
========================================================= */

function render() {

    const latest = latestPublishedResult();

    const cgpa = pick(
        latest,
        ['CGPA', 'cgpa'],
        pick(student, ['CGPA', 'cgpa'])
    );

    const sgpa = pick(
        latest,
        ['SGPA', 'sgpa'],
        pick(student, ['SGPA', 'sgpa'])
    );

    const currentSem = currentSemester();


    /* Dashboard */

    if ($('#cgpa'))
        $('#cgpa').textContent = fmt(cgpa);

    if ($('#sgpa'))
        $('#sgpa').textContent = fmt(sgpa);

    if ($('#year'))
        $('#year').textContent =
            pick(student, [
                'current_year',
                'currentYear',
                'year'
            ]);

    if ($('#branch'))
        $('#branch').textContent =
            pick(student, ['branch']);


    /* IMPORTANT:
       HTML uses #status, not #dashStatus */

    if ($('#status'))
        $('#status').textContent =
            latest ? 'Published' : 'Upcoming';


    if ($('#latest'))
        $('#latest').textContent =
            latest
                ? `Semester ${latest.semester}`
                : 'Latest published';


    /* Academics */

    if ($('#aSem'))
        $('#aSem').textContent =
            currentSem || '—';

    if ($('#aYear'))
        $('#aYear').textContent =
            pick(student, [
                'current_year',
                'currentYear',
                'year'
            ]);

    if ($('#aAdmission'))
        $('#aAdmission').textContent =
            pick(student, [
                'admission_year',
                'admissionYear'
            ]);

    if ($('#aPublished'))
        $('#aPublished').textContent =
            results.length;


    /* Performance */

    if ($('#pCgpa'))
        $('#pCgpa').textContent = fmt(cgpa);

    if ($('#pSgpa'))
        $('#pSgpa').textContent = fmt(sgpa);

    if ($('#pCount'))
        $('#pCount').textContent =
            results.length;


    /* Semester progress */

    let dots = '';

    for (let i = 1; i <= 8; i++) {

        const published = results.some(
            r => num(r.semester) === i
        );

        dots += `
            <i class="${
                published
                    ? 'done'
                    : i === currentSem
                        ? 'current'
                        : ''
            }"></i>
        `;
    }

    if ($('#semesterDots'))
        $('#semesterDots').innerHTML = dots;


    if ($('#progress'))
        $('#progress').textContent =
            `${results.length}/8 published`;


    /* Semester map */

    if ($('#semesterMap')) {

        $('#semesterMap').innerHTML =
            Array.from(
                { length: 8 },
                (_, i) => {

                    const semester = i + 1;

                    const result =
                        results.find(
                            r =>
                                num(r.semester) ===
                                semester
                        );

                    return `
                        <div class="notice">
                            <b>S${semester}</b>

                            <span>
                                ${
                                    result
                                        ? `Published · SGPA ${fmt(
                                            pick(
                                                result,
                                                ['SGPA', 'sgpa']
                                            )
                                        )}`
                                        : semester === currentSem
                                            ? 'Current semester'
                                            : 'Not published'
                                }
                            </span>
                        </div>
                    `;
                }
            ).join('');
    }


    renderResults();
    renderTrend();
    renderExams();
    renderSubjects();
    renderProfile();
    renderNotifications();


    /* Recent result */

    if ($('#recent')) {

        $('#recent').innerHTML =
            latest
                ? `
                    <div>
                        <b>Semester ${latest.semester}</b>

                        <div>
                            SGPA
                            <strong>
                                ${fmt(
                                    pick(
                                        latest,
                                        ['SGPA', 'sgpa']
                                    )
                                )}
                            </strong>

                            · CGPA

                            <strong>
                                ${fmt(
                                    pick(
                                        latest,
                                        ['CGPA', 'cgpa']
                                    )
                                )}
                            </strong>
                        </div>
                    </div>
                `
                : 'No published result yet';
    }


    /* Next exam */

    if ($('#nextExam')) {

        $('#nextExam').innerHTML =
            exams[0]
                ? `
                    <b>
                        ${esc(
                            pick(
                                exams[0],
                                [
                                    'subject',
                                    'subject_name',
                                    'name',
                                    'exam_name'
                                ],
                                'Examination'
                            )
                        )}
                    </b>

                    <br>

                    <small>
                        ${esc(
                            pick(
                                exams[0],
                                [
                                    'exam_date',
                                    'examDate',
                                    'date'
                                ],
                                '—'
                            )
                        )}
                    </small>
                `
                : 'No examination schedule';
    }
}


/* =========================================================
   RESULTS
========================================================= */

function renderResults() {

    if (!$('#resultsList'))
        return;

    if (!results.length) {

        $('#resultsList').innerHTML =
            '<div class="panel pad">No published results yet.</div>';

        return;
    }


    $('#resultsList').innerHTML =
        results.map(result => {

            const subjectList =
                Array.isArray(result.subjects)
                    ? result.subjects
                    : Array.isArray(result.subject_details)
                        ? result.subject_details
                        : [];

            return `
                <article class="panel result">

                    <div class="result-head">

                        <div>
                            <small>
                                SEMESTER ${result.semester}
                            </small>

                            <h3>
                                Semester ${result.semester}
                            </h3>
                        </div>

                        <div class="stats">

                            <span>
                                <small>SGPA</small>

                                <b>
                                    ${fmt(
                                        pick(
                                            result,
                                            ['SGPA', 'sgpa']
                                        )
                                    )}
                                </b>
                            </span>

                            <span>
                                <small>CGPA</small>

                                <b>
                                    ${fmt(
                                        pick(
                                            result,
                                            ['CGPA', 'cgpa']
                                        )
                                    )}
                                </b>
                            </span>

                        </div>

                    </div>


                    <div class="table">

                        <table>

                            <thead>
                                <tr>
                                    <th>CODE</th>
                                    <th>SUBJECT</th>
                                    <th>MARKS</th>
                                    <th>GRADE</th>
                                    <th>CREDITS</th>
                                    <th>STATUS</th>
                                </tr>
                            </thead>

                            <tbody>

                                ${
                                    subjectList.length

                                        ? subjectList.map(subject => `

                                            <tr>

                                                <td>
                                                    ${esc(
                                                        pick(
                                                            subject,
                                                            [
                                                                'code',
                                                                'subject_code',
                                                                'subjectCode'
                                                            ]
                                                        )
                                                    )}
                                                </td>

                                                <td>
                                                    ${esc(
                                                        pick(
                                                            subject,
                                                            [
                                                                'subject',
                                                                'subject_name',
                                                                'subjectName',
                                                                'name'
                                                            ]
                                                        )
                                                    )}
                                                </td>

                                                <td>
                                                    ${esc(
                                                        pick(
                                                            subject,
                                                            [
                                                                'marks',
                                                                'mark',
                                                                'score'
                                                            ]
                                                        )
                                                    )}
                                                </td>

                                                <td>
                                                    ${esc(
                                                        pick(
                                                            subject,
                                                            [
                                                                'grade',
                                                                'grade_point'
                                                            ]
                                                        )
                                                    )}
                                                </td>

                                                <td>
                                                    ${esc(
                                                        pick(
                                                            subject,
                                                            [
                                                                'credits',
                                                                'credit'
                                                            ]
                                                        )
                                                    )}
                                                </td>

                                                <td>
                                                    ${esc(
                                                        pick(
                                                            subject,
                                                            ['status'],
                                                            'PASS'
                                                        )
                                                    )}
                                                </td>

                                            </tr>

                                        `).join('')

                                        : `
                                            <tr>
                                                <td colspan="6">
                                                    No subject details available.
                                                </td>
                                            </tr>
                                        `
                                }

                            </tbody>

                        </table>

                    </div>

                </article>
            `;
        }).join('');
}


/* =========================================================
   PERFORMANCE
========================================================= */

function renderTrend() {

    if (!$('#trend'))
        return;

    const data =
        results.filter(
            r =>
                num(
                    pick(
                        r,
                        ['SGPA', 'sgpa'],
                        null
                    )
                ) !== null
        );


    $('#trend').innerHTML =
        data.length

            ? data.map(result => {

                const sgpa = num(
                    pick(
                        result,
                        ['SGPA', 'sgpa'],
                        0
                    )
                );

                return `
                    <div
                        class="bar"
                        style="height:${Math.max(
                            4,
                            sgpa / 10 * 180
                        )}px"
                    >
                        <b>${sgpa.toFixed(2)}</b>
                    </div>
                `;

            }).join('')

            : '<div>No SGPA history available.</div>';
}


/* =========================================================
   EXAMS
========================================================= */

function renderExams() {

    if (!$('#exams'))
        return;

    $('#exams').innerHTML =
        exams.length

            ? exams.map(exam => `
                <div class="exam">

                    <b>
                        ${esc(
                            pick(
                                exam,
                                [
                                    'subject',
                                    'subject_name',
                                    'name',
                                    'exam_name'
                                ],
                                'Examination'
                            )
                        )}
                    </b>

                    <small>
                        ${esc(
                            pick(
                                exam,
                                [
                                    'exam_date',
                                    'examDate',
                                    'date'
                                ],
                                '—'
                            )
                        )}
                    </small>

                </div>
            `).join('')

            : '<div class="pad">No examination schedule.</div>';
}


/* =========================================================
   SUBJECTS
========================================================= */

function renderSubjects() {

    if (!$('#subjectsBody'))
        return;

    $('#subjectsBody').innerHTML =
        subjects.length

            ? subjects.map(subject => `
                <tr>

                    <td>
                        ${esc(
                            pick(
                                subject,
                                [
                                    'code',
                                    'subject_code',
                                    'subjectCode'
                                ]
                            )
                        )}
                    </td>

                    <td>
                        ${esc(
                            pick(
                                subject,
                                [
                                    'name',
                                    'subject',
                                    'subject_name',
                                    'subjectName'
                                ]
                            )
                        )}
                    </td>

                    <td>
                        ${esc(
                            pick(
                                subject,
                                [
                                    'credits',
                                    'credit'
                                ]
                            )
                        )}
                    </td>

                </tr>
            `).join('')

            : `
                <tr>
                    <td colspan="3">
                        No subject details available.
                    </td>
                </tr>
            `;
}


/* =========================================================
   PROFILE
========================================================= */

function renderProfile() {

    if (!$('#infoGrid'))
        return;

    const s = student;

    const fields = [
        [
            'PRN',
            pick(
                s,
                ['PRN', 'prn'],
                PRN
            )
        ],
        [
            'Email',
            pick(s, ['email'])
        ],
        [
            'Phone',
            pick(s, ['phone'])
        ],
        [
            'College',
            pick(
                s,
                ['college', 'college_name']
            )
        ],
        [
            'Branch',
            pick(s, ['branch'])
        ],
        [
            'Admission Year',
            pick(
                s,
                [
                    'admission_year',
                    'admissionYear'
                ]
            )
        ]
    ];

    $('#infoGrid').innerHTML =
        fields.map(
            field => `
                <div>
                    <small>${field[0]}</small>
                    <b>${esc(field[1])}</b>
                </div>
            `
        ).join('');
}


/* =========================================================
   NOTIFICATIONS
========================================================= */

function renderNotifications() {

    if (!$('#notificationsList'))
        return;

    const unread =
        notifications.filter(
            notification =>
                !Boolean(
                    pick(
                        notification,
                        [
                            'read',
                            'is_read',
                            'isRead'
                        ],
                        false
                    )
                )
        ).length;


    if ($('#badge'))
        $('#badge').textContent =
            unread || '';


    $('#notificationsList').innerHTML =
        notifications.length

            ? notifications.map(notification => {

                const isUnread =
                    !Boolean(
                        pick(
                            notification,
                            [
                                'read',
                                'is_read',
                                'isRead'
                            ],
                            false
                        )
                    );

                return `
                    <article
                        class="notification ${
                            isUnread ? 'unread' : ''
                        }"
                    >

                        <h3>
                            ${esc(
                                pick(
                                    notification,
                                    [
                                        'title',
                                        'subject',
                                        'name'
                                    ],
                                    'Notification'
                                )
                            )}
                        </h3>

                        <p>
                            ${esc(
                                pick(
                                    notification,
                                    [
                                        'message',
                                        'body',
                                        'description'
                                    ],
                                    ''
                                )
                            )}
                        </p>

                    </article>
                `;

            }).join('')

            : `
                <div class="panel pad">
                    No notifications.
                </div>
            `;
}


/* =========================================================
   NAVIGATION
========================================================= */

function nav(page) {

    document
        .querySelectorAll('.page')
        .forEach(
            element =>
                element.classList.toggle(
                    'hidden',
                    element.id !== page
                )
        );


    document
        .querySelectorAll('nav button')
        .forEach(
            button =>
                button.classList.toggle(
                    'active',
                    button.dataset.page === page
                )
        );


    const titles = {
        dashboard: 'Dashboard',
        academics: 'My Academics',
        results: 'My Results',
        performance: 'Performance',
        examination: 'Examination',
        subjects: 'Subjects',
        profile: 'Profile',
        notifications: 'Notifications',
        help: 'Help & FAQ'
    };


    if ($('#title'))
        $('#title').textContent =
            titles[page] || 'Dashboard';


    if (
        window.innerWidth < 900 &&
        $('aside')
    ) {
        $('aside').classList.remove('open');
    }
}


/* =========================================================
   EVENTS
========================================================= */

document
    .querySelectorAll('nav button[data-page]')
    .forEach(
        button =>
            button.onclick = () =>
                nav(button.dataset.page)
    );


if ($('#menu')) {

    $('#menu').onclick = () => {

        if ($('aside'))
            $('aside').classList.toggle('open');

    };
}


if ($('#logout')) {

    $('#logout').onclick = () => {

        sessionStorage.removeItem(
            'resultday_prn'
        );

        location.reload();
    };
}


/* =========================================================
   LOGIN
========================================================= */

if ($('#loginForm')) {

    $('#loginForm').onsubmit = async event => {

        event.preventDefault();

        if ($('#loginMsg'))
            $('#loginMsg').textContent = '';

        try {

            const prn =
                $('#prn').value.trim();

            const data =
                await api(
                    '/login',
                    {
                        method: 'POST',
                        body: JSON.stringify({
                            prn,
                            password:
                                $('#password').value
                        })
                    }
                );


            PRN = prn;

            sessionStorage.setItem(
                'resultday_prn',
                PRN
            );


            $('#login').classList.add(
                'hidden'
            );

            $('#portal').classList.remove(
                'hidden'
            );


            identity(
                data.student || {}
            );

            await load();

            nav('dashboard');

        } catch (error) {

            if ($('#loginMsg'))
                $('#loginMsg').textContent =
                    error.message;
        }
    };
}


/* =========================================================
   INITIAL LOAD
========================================================= */

if (PRN) {

    $('#login').classList.add('hidden');

    $('#portal').classList.remove('hidden');

    load();

} else {

    $('#portal').classList.add('hidden');
}
