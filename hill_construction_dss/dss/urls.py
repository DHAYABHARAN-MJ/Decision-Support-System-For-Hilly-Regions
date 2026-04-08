from django.urls import path
from .views import AssessView, ScoreOnlyView, SPTView, ParameterRulesView, CompoundRulesView

urlpatterns = [
    path("assess/",         AssessView.as_view(),        name="dss-assess"),
    path("score/",          ScoreOnlyView.as_view(),      name="dss-score"),
    path("spt/",            SPTView.as_view(),            name="dss-spt"),
    path("rules/",          ParameterRulesView.as_view(), name="dss-rules"),
    path("compound-rules/", CompoundRulesView.as_view(),  name="dss-compound"),
]
