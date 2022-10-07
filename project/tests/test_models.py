from django.test import TestCase
from project.models import Project, Domain, SubDomain
from django.utils import timezone
# models test


class ProjectTest(TestCase):

    def create_project(self, name="test project", api_url="http://www.test_api_url.com/",
                       html_url="http://www.test_html_url.com", domain="test_domain", subdomain="test_subdomain"):
        return Project.objects.create(name=name, api_url=api_url, html_url=html_url,
                                      domain=Domain.objects.create(name="test_domain"),
                                      subdomain=SubDomain.objects.create(name="test_subdomain"))

    def test_project_creation(self):
        w = self.create_project()
        self.assertTrue(isinstance(w, Project))
        self.assertEqual(w.name, "test project")
        self.assertEqual(w.api_url, "http://www.test_api_url.com/")
        self.assertEqual(w.html_url, "http://www.test_html_url.com")
        self.assertTrue(isinstance(w.domain, Domain))
        self.assertTrue(isinstance(w.subdomain, SubDomain))
