from flask import Flask, request, jsonify
import uuid
import requests
import xml.etree.ElementTree as ET

app = Flask(__name__)
jobs = []

@app.route('/jobs', methods=['POST'])
def add_job():
    job_data = request.get_json()
    job_data['id'] = str(uuid.uuid4())
    jobs.append(job_data)
    return jsonify({"message": "Job added successfully", "job": job_data}), 201

def parse_skills(xml_skills):
    root = ET.fromstring(xml_skills)
    return [skill.text for skill in root.findall('skill')]

def fetch_external_jobs():
    try:
        response = requests.get('http://localhost:8080/jobs')
        if response.status_code == 200:
            external_jobs_data = response.json()
            external_jobs = []
            for country, jobs in external_jobs_data.items():
                for job in jobs:
                    job_name, salary, skills_xml = job
                    job_data = {
                        "title": job_name,
                        "salary": salary,
                        "skills": parse_skills(skills_xml),
                        "country": country
                    }
                    external_jobs.append(job_data)
            return external_jobs
    except requests.exceptions.RequestException as e:
        print(f"Error fetching external jobs: {e}")
    return []

@app.route('/jobs', methods=['GET'])
def search_jobs():
    title = request.args.get('title')
    company = request.args.get('company')
    country = request.args.get('country')

    internal_results = [job for job in jobs if
                        (not title or title.lower() in job.get('title', '').lower()) and
                        (not company or company.lower() in job.get('company', '').lower()) and
                        (not country or country.lower() in job.get('country', '').lower())]

    external_jobs = fetch_external_jobs()
    external_results = [job for job in external_jobs if
                        (not title or title.lower() in job.get('title', '').lower()) and
                        (not country or country.lower() in job.get('country', '').lower())]

    combined_results = internal_results + external_results
    return jsonify({"results": combined_results}), 200

if __name__ == '__main__':
    app.run(debug=True)
