/* =========================================================
   RESULT DAY — ADMIN PORTAL
========================================================= */


/* =========================================================
   CONFIGURATION
========================================================= */

const API_BASE_URL =
    "http://127.0.0.1:5000";




/* =========================================================
   ELEMENT HELPERS
========================================================= */

const $ = (id) => document.getElementById(id);

const qsa = (selector) =>
    document.querySelectorAll(selector);


/* =========================================================
   LOGIN
========================================================= */

const loginScreen = $("loginScreen");
const adminApp = $("adminApp");


function isLoggedIn() {
    return sessionStorage.getItem(
        "resultDayAdmin"
    ) === "true";
}


function showAdminApp() {

    loginScreen.classList.add("hidden");
    adminApp.classList.remove("hidden");

    loadDashboard();

}


function showLogin() {

    adminApp.classList.add("hidden");
    loginScreen.classList.remove("hidden");

}

$("loginForm").addEventListener(
    "submit",
    async function (event) {

        event.preventDefault();

        const username =
            $("adminUsername").value.trim();

        const password =
            $("adminPassword").value;

        const message =
            $("loginMessage");

        message.textContent =
            "Signing in...";

        try {

            const data =
                await apiRequest(
                    "/admin/login",
                    {
                        method: "POST",

                        body: JSON.stringify({
                            username: username,
                            password: password
                        })
                    }
                );

            if (data.status === "success") {

                sessionStorage.setItem(
                    "resultDayAdmin",
                    "true"
                );

                message.textContent = "";

                showAdminApp();

                showToast(
                    "Admin login successful."
                );

            } else {

                message.textContent =
                    data.message ||
                    "Invalid administrator credentials.";

            }

        } catch (error) {

            console.error(
                "Admin login error:",
                error
            );

            message.textContent =
                error.message ||
                "Invalid administrator credentials.";

        }

    }
);


$("togglePassword").addEventListener(
    "click",
    function () {

        const passwordInput =
            $("adminPassword");

        if (
            passwordInput.type === "password"
        ) {

            passwordInput.type = "text";
            this.textContent = "Hide";

        } else {

            passwordInput.type = "password";
            this.textContent = "Show";

        }

    }
);


$("logoutBtn").addEventListener(
    "click",
    function () {

        sessionStorage.removeItem(
            "resultDayAdmin"
        );

        showLogin();

    }
);


/* =========================================================
   NAVIGATION
========================================================= */

const pageTitles = {

    dashboard: [
        "Admin Dashboard",
        "Result Day system overview"
    ],

    release: [
        "Result Release",
        "Schedule and publish student results"
    ],

    students: [
        "Students",
        "Student accounts and academic information"
    ],

    results: [
        "Results",
        "Published academic records"
    ],

    notifications: [
        "Notifications",
        "Student communication"
    ],

    traffic: [
        "Traffic & ALB",
        "Application Load Balancer monitoring"
    ],

    compute: [
        "EC2 & Scaling",
        "AWS compute infrastructure"
    ],

    monitoring: [
        "Monitoring",
        "Application and infrastructure health"
    ]

};


function getSectionElement(sectionName) {

    if (sectionName === "dashboard") {
        return $("dashboard");
    }

    return $(
        "page-" + sectionName
    );

}


function openSection(sectionName) {

    qsa(".page-section").forEach(
        section => {
            section.classList.remove(
                "active"
            );
        }
    );

    qsa(".nav-item").forEach(
        item => {
            item.classList.remove(
                "active"
            );
        }
    );

    const section =
        getSectionElement(sectionName);

    if (section) {

        section.classList.add(
            "active"
        );

    }

    const navItem =
        document.querySelector(
            `.nav-item[data-section="${sectionName}"]`
        );

    if (navItem) {

        navItem.classList.add(
            "active"
        );

    }

    const title =
        pageTitles[sectionName];

    if (title) {

        $("pageTitle").textContent =
            title[0];

        $("pageSubtitle").textContent =
            title[1];

    }


    /* -----------------------------------------------------
       Dynamic page loading
    ----------------------------------------------------- */

    if (sectionName === "dashboard") {
        loadDashboard();
    }

    if (sectionName === "release") {
        loadSchedules();
    }

    if (sectionName === "students") {
        loadStudents();
    }

    if (sectionName === "traffic") {
        loadTraffic();
    }

    if (sectionName === "compute") {
        loadCompute();
    }

    if (sectionName === "monitoring") {
        loadMonitoring();
    }

}


qsa(".nav-item").forEach(
    item => {

        item.addEventListener(
            "click",
            function () {

                openSection(
                    this.dataset.section
                );

            }
        );

    }
);


qsa("[data-section]").forEach(
    item => {

        if (
            !item.classList.contains(
                "nav-item"
            )
        ) {

            item.addEventListener(
                "click",
                function () {

                    openSection(
                        this.dataset.section
                    );

                }
            );

        }

    }
);


$("menuBtn").addEventListener(
    "click",
    function () {

        $("sidebar").classList.toggle(
            "open"
        );

    }
);


/* =========================================================
   API HELPER
========================================================= */

async function apiRequest(
    endpoint,
    options = {}
) {

    const response =
        await fetch(
            `${API_BASE_URL}${endpoint}`,
            {
                ...options,

                headers: {
                    "Content-Type":
                        "application/json",

                    ...(options.headers || {})
                }
            }
        );

    let data = {};

    try {

        data =
            await response.json();

    } catch {

        data = {};

    }

    if (!response.ok) {

        throw new Error(
            data.message ||
            `Request failed (${response.status})`
        );

    }

    return data;

}


/* =========================================================
   TOAST
========================================================= */

function showToast(message) {

    const toast = $("toast");

    toast.textContent = message;

    toast.classList.add("show");

    setTimeout(
        () => {
            toast.classList.remove(
                "show"
            );
        },
        2500
    );

}


/* =========================================================
   DASHBOARD
========================================================= */

async function loadDashboard() {

    try {

        const data =
            await apiRequest(
                "/admin/dashboard"
            );

        console.log(
            "Admin dashboard:",
            data
        );

        const students =
            Number(
                data.total_students ?? 0
            );

        const published =
            Number(
                data.published_results ?? 0
            );

        const scheduled =
            Number(
                data.scheduled_results ?? 0
            );

        const pending =
            Number(
                data.pending_results ??
                scheduled
            );

        const releasePercent =
            Number(
                data.release_percent ?? 0
            );


        $("totalStudents").textContent =
            students;

        $("publishedResults").textContent =
            published;

        $("scheduledResults").textContent =
            scheduled;

        $("dashPublished").textContent =
            published;

        $("dashScheduled").textContent =
            scheduled;

        $("dashPending").textContent =
            pending;

        $("releasePercent").textContent =
            `${releasePercent}%`;


    } catch (error) {

        console.error(
            "Dashboard error:",
            error
        );

    }


    await checkBackendHealth();

}


/* =========================================================
   BACKEND / DATABASE HEALTH
========================================================= */

async function checkBackendHealth() {

    /* -----------------------------------------------------
       Flask
    ----------------------------------------------------- */

    try {

        const data =
            await apiRequest(
                "/health"
            );

        if (
            data.status === "healthy"
        ) {

            $("backendStatus").textContent =
                "Healthy";

            $("backendStatus").className =
                "badge success";

            $("flaskHealth").textContent =
                "Healthy";

            $("flaskHealth").style.color =
                "var(--success)";

            $("monitorBackend").textContent =
                "Healthy";

        } else {

            throw new Error(
                "Backend unhealthy"
            );

        }

    } catch {

        $("backendStatus").textContent =
            "Offline";

        $("backendStatus").className =
            "badge danger";

        $("flaskHealth").textContent =
            "Offline";

        $("flaskHealth").style.color =
            "var(--danger)";

        $("monitorBackend").textContent =
            "Offline";

    }


    /* -----------------------------------------------------
       DynamoDB
    ----------------------------------------------------- */

    try {

        await apiRequest(
            "/test-dynamodb"
        );

        $("dynamoHealth").textContent =
            "Connected";

        $("dynamoHealth").style.color =
            "var(--success)";

        $("monitorDatabase").textContent =
            "Connected";

    } catch {

        $("dynamoHealth").textContent =
            "Unavailable";

        $("dynamoHealth").style.color =
            "var(--danger)";

        $("monitorDatabase").textContent =
            "Unavailable";

    }

}


/* =========================================================
   RESULT SCHEDULING
========================================================= */

$("scheduleForm").addEventListener(
    "submit",
    async function (event) {

        event.preventDefault();

        try {

            const batch =
                $("scheduleBatch")
                    .value
                    .trim();

            const branch =
                $("scheduleBranch")
                    .value
                    .trim();

            const semester =
                $("scheduleSemester")
                    .value;

            const dateTime =
                $("scheduleReleaseTime")
                    .value;

            if (
                !batch ||
                !branch ||
                !semester ||
                !dateTime
            ) {

                showToast(
                    "Please complete all schedule fields."
                );

                return;

            }

            const releaseDate =
                new Date(dateTime);

            if (
                Number.isNaN(
                    releaseDate.getTime()
                )
            ) {

                showToast(
                    "Invalid release date/time."
                );

                return;

            }

            const release_datetime =
                releaseDate.toISOString();


            const data =
                await apiRequest(
                    "/admin/results/schedule",
                    {
                        method: "POST",

                        body: JSON.stringify({

                            batch,

                            branch,

                            semester,

                            release_datetime

                        })
                    }
                );


            console.log(
                "Schedule response:",
                data
            );


            showToast(
                data.message ||
                "Batch result scheduled successfully."
            );


            this.reset();

            await loadSchedules();

            await loadDashboard();


        } catch (error) {

            console.error(
                "Schedule error:",
                error
            );

            showToast(
                error.message ||
                "Unable to schedule result."
            );

        }

    }
);


/* =========================================================
   LOAD RELEASE SCHEDULES
========================================================= */

async function loadSchedules() {

    const tbody =
        $("scheduleTableBody");

    tbody.innerHTML = `
        <tr>
            <td colspan="5"
                class="empty-state">
                Loading...
            </td>
        </tr>
    `;


    try {

        const data =
            await apiRequest(
                "/admin/results/schedule"
            );

        console.log(
            "Schedules:",
            data
        );


        const schedules =
            data.results || [];


        if (
            !Array.isArray(
                schedules
            ) ||
            schedules.length === 0
        ) {

            tbody.innerHTML = `
                <tr>
                    <td colspan="5"
                        class="empty-state">
                        No scheduled results found.
                    </td>
                </tr>
            `;

            return;

        }


        tbody.innerHTML =
            schedules.map(
                item => {

                    const status =
                        item.release_status ||
                        "SCHEDULED";


                    return `
                        <tr>

                            <td>
                                ${escapeHtml(
                                    item.batch ||
                                    "—"
                                )}
                            </td>

                            <td>
                                ${escapeHtml(
                                    item.branch ||
                                    "—"
                                )}
                            </td>

                            <td>
                                Semester
                                ${escapeHtml(
                                    String(
                                        item.semester ||
                                        "—"
                                    )
                                )}
                            </td>

                            <td>

                                <span class="badge ${
                                    status ===
                                    "PUBLISHED"
                                        ? "success"
                                        : "warning"
                                }">

                                    ${escapeHtml(
                                        status
                                    )}

                                </span>

                            </td>

                            <td>
                                ${formatDate(
                                    item.release_datetime
                                )}
                            </td>

                        </tr>
                    `;

                }
            ).join("");


    } catch (error) {

        console.error(
            "Schedule loading error:",
            error
        );

        tbody.innerHTML = `
            <tr>
                <td colspan="5"
                    class="empty-state">
                    Unable to load schedules.
                </td>
            </tr>
        `;

    }

}


$("loadSchedulesBtn").addEventListener(
    "click",
    loadSchedules
);


/* =========================================================
   PUBLISH RESULT
========================================================= */

$("publishForm").addEventListener(
    "submit",
    async function (event) {

        event.preventDefault();

        try {

            const batch =
                $("publishBatch")
                    .value
                    .trim();

            const branch =
                $("publishBranch")
                    .value
                    .trim();

            const semester =
                $("publishSemester")
                    .value;


            if (
                !batch ||
                !branch ||
                !semester
            ) {

                showToast(
                    "Please complete all publish fields."
                );

                return;

            }


            const data =
                await apiRequest(
                    "/admin/results/publish",
                    {
                        method: "POST",

                        body: JSON.stringify({

                            batch,

                            branch,

                            semester

                        })
                    }
                );


            console.log(
                "Publish response:",
                data
            );


            showToast(
                data.message ||
                "Batch result published successfully."
            );


            this.reset();

            await loadSchedules();

            await loadDashboard();


        } catch (error) {

            console.error(
                "Publish error:",
                error
            );

            showToast(
                error.message ||
                "Unable to publish result."
            );

        }

    }
);


/* =========================================================
   STUDENTS
========================================================= */

async function loadStudents() {

    const tbody =
        $("studentTableBody");

    tbody.innerHTML = `
        <tr>
            <td colspan="6"
                class="empty-state">
                Loading...
            </td>
        </tr>
    `;


    try {

        const data =
            await apiRequest(
                "/admin/students"
            );


        const students =
            data.students || [];


        if (
            !Array.isArray(
                students
            ) ||
            students.length === 0
        ) {

            tbody.innerHTML = `
                <tr>
                    <td colspan="6"
                        class="empty-state">
                        No students found.
                    </td>
                </tr>
            `;

            return;

        }


        renderStudents(
            students
        );


    } catch (error) {

        console.error(
            "Student loading error:",
            error
        );

        tbody.innerHTML = `
            <tr>
                <td colspan="6"
                    class="empty-state">
                    Unable to load students.
                </td>
            </tr>
        `;

    }

}


function renderStudents(
    students
) {

    const tbody =
        $("studentTableBody");


    tbody.innerHTML =
        students.map(
            student => {

                const active =
                    student.account_active ===
                    true;


                return `
                    <tr>

                        <td>
                            ${escapeHtml(
                                student.PRN ||
                                "—"
                            )}
                        </td>

                        <td>
                            ${escapeHtml(
                                student.name ||
                                "—"
                            )}
                        </td>

                        <td>
                            ${escapeHtml(
                                student.email ||
                                "—"
                            )}
                        </td>

                        <td>
                            ${escapeHtml(
                                student.branch ||
                                "—"
                            )}
                        </td>

                        <td>
                            ${escapeHtml(
                                String(
                                    student.current_year ??
                                    "—"
                                )
                            )}
                        </td>

                        <td>

                            <span class="badge ${
                                active
                                    ? "success"
                                    : "neutral"
                            }">

                                ${
                                    active
                                        ? "ACTIVE"
                                        : "INACTIVE"
                                }

                            </span>

                        </td>

                    </tr>
                `;

            }
        ).join("");

}


$("refreshStudentsBtn").addEventListener(
    "click",
    loadStudents
);


/* =========================================================
   STUDENT SEARCH
========================================================= */

$("studentSearch").addEventListener(
    "input",
    function () {

        const search =
            this.value
                .trim()
                .toLowerCase();


        qsa(
            "#studentTableBody tr"
        ).forEach(
            row => {

                row.style.display =
                    row.textContent
                        .toLowerCase()
                        .includes(search)
                        ? ""
                        : "none";

            }
        );

    }
);


/* =========================================================
   RESULTS SEARCH
========================================================= */

$("searchResultsBtn").addEventListener(
    "click",
    async function () {

        const prn =
            $("resultSearchPrn")
                .value
                .trim();

        const output =
            $("resultSearchOutput");


        if (!prn) {

            output.innerHTML = `
                <div class="empty-state">
                    Enter a PRN first.
                </div>
            `;

            return;

        }


        output.innerHTML = `
            <div class="empty-state">
                Loading results...
            </div>
        `;


        try {

            const data =
                await apiRequest(
                    `/results/${encodeURIComponent(prn)}`
                );


            const results =
                data.results || [];


            if (
                results.length === 0
            ) {

                output.innerHTML = `
                    <div class="empty-state">
                        No published results found.
                    </div>
                `;

                return;

            }


            output.innerHTML = `
                <div class="table-wrapper">

                    <table>

                        <thead>

                            <tr>
                                <th>Semester</th>
                                <th>Year</th>
                                <th>SGPA</th>
                                <th>CGPA</th>
                                <th>Status</th>
                                <th>Release Date</th>
                            </tr>

                        </thead>

                        <tbody>

                            ${results.map(
                                result => `

                                <tr>

                                    <td>
                                        Semester
                                        ${escapeHtml(
                                            result.semester ||
                                            "—"
                                        )}
                                    </td>

                                    <td>
                                        ${escapeHtml(
                                            result.year ||
                                            "—"
                                        )}
                                    </td>

                                    <td>
                                        ${escapeHtml(
                                            result.SGPA ||
                                            result.sgpa ||
                                            "—"
                                        )}
                                    </td>

                                    <td>
                                        ${escapeHtml(
                                            result.CGPA ||
                                            result.cgpa ||
                                            "—"
                                        )}
                                    </td>

                                    <td>

                                        <span class="badge success">
                                            ${escapeHtml(
                                                result.status ||
                                                "PUBLISHED"
                                            )}
                                        </span>

                                    </td>

                                    <td>
                                        ${formatDate(
                                            result.release_datetime
                                        )}
                                    </td>

                                </tr>

                            `
                            ).join("")}

                        </tbody>

                    </table>

                </div>
            `;


        } catch (error) {

            console.error(
                "Results search error:",
                error
            );

            output.innerHTML = `
                <div class="empty-state">
                    ${escapeHtml(
                        error.message
                    )}
                </div>
            `;

        }

    }
);


/* =========================================================
   NOTIFICATIONS
========================================================= */

$("notificationForm").addEventListener(
    "submit",
    async function (event) {

        event.preventDefault();


        const status =
            $("notificationStatus");


        const prn =
            $("notificationPrn")
                .value
                .trim();


        const type =
            $("notificationType")
                .value;


        const message =
            $("notificationMessage")
                .value
                .trim();


        if (
            !prn ||
            !message
        ) {

            status.textContent =
                "PRN and message are required.";

            status.style.color =
                "var(--danger)";

            return;

        }


        status.textContent =
            "Sending...";

        status.style.color =
            "var(--muted)";


        try {

            const data =
                await apiRequest(
                    `/notifications/${encodeURIComponent(prn)}`,
                    {
                        method: "POST",

                        body: JSON.stringify({

                            type,

                            message

                        })
                    }
                );


            status.textContent =
                data.message ||
                "Notification sent.";

            status.style.color =
                "var(--success)";


            showToast(
                "Notification sent."
            );


            this.reset();


            await loadDashboard();


        } catch (error) {

            console.error(
                "Notification error:",
                error
            );

            status.textContent =
                error.message;

            status.style.color =
                "var(--danger)";

        }

    }
);


/* =========================================================
   TRAFFIC — AWS DYNAMIC
========================================================= */

async function loadTraffic() {

    try {

        const data =
            await apiRequest(
                "/admin/aws/traffic"
            );


        console.log(
            "AWS traffic:",
            data
        );


        $("trafficAlbStatus").textContent =
            data.alb_status ||
            "Unknown";


        $("trafficAlbStatus").style.color =
            data.healthy_targets > 0
                ? "var(--success)"
                : "var(--danger)";


        $("requestsPerMinute").textContent =
            Number(
                data.requests_per_minute ?? 0
            );


        $("healthyTargets").textContent =
            `${data.healthy_targets ?? 0} / ${
                data.total_targets ?? 0
            }`;


        $("albHealth").textContent =
            data.alb_status ||
            "Unknown";


        $("monitorAlb").textContent =
            data.alb_status ||
            "Unknown";


    } catch (error) {

        console.error(
            "Traffic error:",
            error
        );


        $("trafficAlbStatus").textContent =
            "Unavailable";

        $("trafficAlbStatus").style.color =
            "var(--danger)";

        $("requestsPerMinute").textContent =
            "—";

        $("healthyTargets").textContent =
            "—";

        $("albHealth").textContent =
            "Unavailable";

        $("monitorAlb").textContent =
            "Unavailable";

    }

}


$("refreshTrafficBtn").addEventListener(
    "click",
    async function () {

        await loadTraffic();

        showToast(
            "Traffic information refreshed."
        );

    }
);


/* =========================================================
   COMPUTE — AWS DYNAMIC
========================================================= */

async function loadCompute() {

    try {

        const data =
            await apiRequest(
                "/admin/aws/compute"
            );


        console.log(
            "AWS compute:",
            data
        );


        $("desiredCapacity").textContent =
            data.desired_capacity ?? "—";


        $("minCapacity").textContent =
            data.min_size ?? "—";


        $("maxCapacity").textContent =
            data.max_size ?? "—";


        const instances =
            data.instances || [];


        if (
            instances.length === 0
        ) {

            $("instanceList").innerHTML = `

                <div class="instance-card">

                    <div class="instance-main">

                        <div class="instance-icon">
                            EC2
                        </div>

                        <div>

                            <strong>
                                No ASG instances running
                            </strong>

                            <span>
                                Desired capacity:
                                ${escapeHtml(
                                    String(
                                        data.desired_capacity ??
                                        0
                                    )
                                )}
                            </span>

                        </div>

                    </div>

                    <span class="badge neutral">
                        Stopped
                    </span>

                </div>

            `;

            return;

        }


        $("instanceList").innerHTML =
            instances.map(
                instance => {

                    const state =
                        instance.state ||
                        "unknown";


                    const healthy =
                        state ===
                        "running";


                    return `

                        <div class="instance-card">

                            <div class="instance-main">

                                <div class="instance-icon">
                                    EC2
                                </div>

                                <div>

                                    <strong>
                                        ${escapeHtml(
                                            instance.instance_id ||
                                            "Unknown instance"
                                        )}
                                    </strong>

                                    <span>
                                        ${
                                            escapeHtml(
                                                instance.availability_zone ||
                                                "Unknown AZ"
                                            )
                                        }

                                        ${
                                            instance.private_ip
                                                ? " • " +
                                                  escapeHtml(
                                                      instance.private_ip
                                                  )
                                                : ""
                                        }

                                    </span>

                                </div>

                            </div>

                            <span class="badge ${
                                healthy
                                    ? "success"
                                    : "warning"
                            }">

                                ${escapeHtml(
                                    state
                                )}

                            </span>

                        </div>

                    `;

                }
            ).join("");


    } catch (error) {

        console.error(
            "Compute error:",
            error
        );


        $("desiredCapacity").textContent =
            "—";

        $("minCapacity").textContent =
            "—";

        $("maxCapacity").textContent =
            "—";


        $("instanceList").innerHTML = `

            <div class="empty-state">
                Unable to load AWS compute information.
            </div>

        `;

    }

}


$("refreshComputeBtn").addEventListener(
    "click",
    async function () {

        await loadCompute();

        showToast(
            "Compute information refreshed."
        );

    }
);


/* =========================================================
   EC2 / ASG START
========================================================= */

$("startEc2Btn").addEventListener(
    "click",
    async function () {

        const button =
            $("startEc2Btn");


        button.disabled = true;
        button.textContent =
            "Starting...";


        $("ec2ActionMessage").textContent =
            "Starting Result Day infrastructure...";


        $("ec2ActionMessage").style.color =
            "var(--warning)";


        try {

            const response =
                await apiRequest(
                    "/admin/aws/ec2/start",
                    {
                        method: "POST"
                    }
                );


            $("ec2ActionMessage").textContent =
                response.message ||
                "Infrastructure start requested.";


            $("ec2ActionMessage").style.color =
                "var(--success)";


            showToast(
                "Start request accepted."
            );


            /*
               AWS needs time to launch instances.
               Refresh after a short delay.
            */

            setTimeout(
                loadCompute,
                5000
            );


        } catch (error) {

            console.error(
                "Start error:",
                error
            );


            $("ec2ActionMessage").textContent =
                error.message ||
                "Failed to start infrastructure.";


            $("ec2ActionMessage").style.color =
                "var(--danger)";


            showToast(
                error.message ||
                "Failed to start infrastructure."
            );


        } finally {

            button.disabled = false;

            button.textContent =
                "▶ Start EC2";

        }

    }
);


/* =========================================================
   EC2 / ASG STOP
========================================================= */

$("stopEc2Btn").addEventListener(
    "click",
    async function () {

        const confirmed =
            confirm(
                "Stop Result Day infrastructure?\n\n" +
                "This will set the Auto Scaling Group " +
                "minimum and desired capacity to 0.\n\n" +
                "The current ASG-managed EC2 instances " +
                "will be terminated."
            );


        if (!confirmed) {
            return;
        }


        const button =
            $("stopEc2Btn");


        button.disabled = true;

        button.textContent =
            "Stopping...";


        $("ec2ActionMessage").textContent =
            "Stopping Result Day infrastructure...";


        $("ec2ActionMessage").style.color =
            "var(--warning)";


        try {

            const response =
                await apiRequest(
                    "/admin/aws/ec2/stop",
                    {
                        method: "POST"
                    }
                );


            $("ec2ActionMessage").textContent =
                response.message ||
                "Infrastructure stop requested.";


            $("ec2ActionMessage").style.color =
                "var(--success)";


            showToast(
                "Stop request accepted."
            );


            setTimeout(
                loadCompute,
                5000
            );


        } catch (error) {

            console.error(
                "Stop error:",
                error
            );


            $("ec2ActionMessage").textContent =
                error.message ||
                "Failed to stop infrastructure.";


            $("ec2ActionMessage").style.color =
                "var(--danger)";


            showToast(
                error.message ||
                "Failed to stop infrastructure."
            );


        } finally {

            button.disabled = false;

            button.textContent =
                "■ Stop EC2";

        }

    }
);


/* =========================================================
   MONITORING — AWS DYNAMIC
========================================================= */

async function loadMonitoring() {

    try {

        const data =
            await apiRequest(
                "/admin/aws/monitoring"
            );


        console.log(
            "AWS monitoring:",
            data
        );


        $("monitorBackend").textContent =
            data.backend ||
            "Unknown";


        $("monitorDatabase").textContent =
            data.database ||
            "Unknown";


        $("monitorAlb").textContent =
            data.alb ||
            "Unknown";


        $("monitorScaling").textContent =
            data.scaling ||
            "Unknown";


        /*
           Keep the normal health styling.
        */

        $("monitorBackend").style.color =
            data.backend === "Healthy"
                ? "var(--success)"
                : "var(--danger)";


        $("monitorDatabase").style.color =
            data.database === "Healthy"
                ? "var(--success)"
                : "var(--danger)";


        $("monitorAlb").style.color =
            data.alb === "Healthy"
                ? "var(--success)"
                : "var(--danger)";


        $("monitorScaling").style.color =
            data.scaling === "Active"
                ? "var(--success)"
                : "var(--warning)";


    } catch (error) {

        console.error(
            "Monitoring error:",
            error
        );


        $("monitorBackend").textContent =
            "Unavailable";

        $("monitorDatabase").textContent =
            "Unavailable";

        $("monitorAlb").textContent =
            "Unavailable";

        $("monitorScaling").textContent =
            "Unavailable";

    }

}


$("refreshMonitoringBtn").addEventListener(
    "click",
    async function () {

        await loadMonitoring();

        showToast(
            "Monitoring refreshed."
        );

    }
);


/* =========================================================
   GLOBAL REFRESH
========================================================= */

$("refreshBtn").addEventListener(
    "click",
    async function () {

        const activeSection =
            document.querySelector(
                ".page-section.active"
            );


        if (!activeSection) {
            return;
        }


        let sectionName =
            activeSection.id;


        if (
            sectionName !==
            "dashboard"
        ) {

            sectionName =
                sectionName.replace(
                    /^page-/,
                    ""
                );

        }


        openSection(
            sectionName
        );


        showToast(
            "Information refreshed."
        );

    }
);


/* =========================================================
   HELPERS
========================================================= */

function formatDate(value) {

    if (!value) {
        return "—";
    }


    const date =
        new Date(value);


    if (
        Number.isNaN(
            date.getTime()
        )
    ) {

        return String(value);

    }


    return date.toLocaleString(
        "en-IN",
        {
            dateStyle: "medium",
            timeStyle: "short"
        }
    );

}


function escapeHtml(value) {

    return String(value)

        .replaceAll(
            "&",
            "&amp;"
        )

        .replaceAll(
            "<",
            "&lt;"
        )

        .replaceAll(
            ">",
            "&gt;"
        )

        .replaceAll(
            '"',
            "&quot;"
        )

        .replaceAll(
            "'",
            "&#039;"
        );

}


/* =========================================================
   INITIALIZATION
========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    function () {

        if (
            isLoggedIn()
        ) {

            showAdminApp();

        }

    }
);