# dss/views.py  v3
import json
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .engine import DSSEngine
from .validators import validate_params, FIELD_RULES


def _cors(r):
    r["Access-Control-Allow-Origin"] = "*"
    return r

def _parse(request):
    try:
        return json.loads(request.body), None
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None, JsonResponse({"error": "Invalid JSON body."}, status=400)


@method_decorator(csrf_exempt, name="dispatch")
class AssessView(View):
    def post(self, request):
        body, err = _parse(request)
        if err: return err
        cleaned, errors = validate_params(body)
        if errors: return _cors(JsonResponse({"errors": errors}, status=422))
        return _cors(JsonResponse(DSSEngine.assess(cleaned), status=200))

    def get(self, request):
        return _cors(JsonResponse({"endpoint": "POST /api/dss/assess/",
            "required_fields": {f: str(r) for f, r in FIELD_RULES.items()}}))

    def options(self, request):
        r = JsonResponse({})
        r["Access-Control-Allow-Origin"] = "*"
        r["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        r["Access-Control-Allow-Headers"] = "Content-Type"
        return r


@method_decorator(csrf_exempt, name="dispatch")
class ScoreOnlyView(View):
    def post(self, request):
        body, err = _parse(request)
        if err: return err
        cleaned, errors = validate_params(body)
        if errors: return _cors(JsonResponse({"errors": errors}, status=422))
        r = DSSEngine.assess(cleaned)
        return _cors(JsonResponse({"score": r["score"], "verdict": r["verdict"]["verdict"],
            "color": r["verdict"]["color"], "action": r["verdict"]["action"]}))


@method_decorator(csrf_exempt, name="dispatch")
class SPTView(View):
    """POST /api/dss/spt/ — Convert SPT N-value to bearing capacity."""
    def post(self, request):
        body, err = _parse(request)
        if err: return err
        try:
            n_value   = float(body.get("n_value", 0))
            depth_m   = float(body.get("depth_m", 1.5))
            soil_type = str(body.get("soil_type", "sandy")).lower()
        except (TypeError, ValueError):
            return _cors(JsonResponse({"error": "n_value and depth_m must be numbers."}, status=400))
        if not (1 <= n_value <= 100):
            return _cors(JsonResponse({"error": "n_value must be between 1 and 100."}, status=422))
        result = DSSEngine.spt_to_bearing(n_value, depth_m, soil_type)
        return _cors(JsonResponse(result))


class ParameterRulesView(View):
    def get(self, request):
        return _cors(JsonResponse({
            "total_parameters": 15,
            "note": "elevation in metres AMSL, moisture_content in %, building_load in kN/m2",
            "foundation_types": ["pile","raft","stepped","shallow","isolated","combined","under_reamed"],
            "verdict_ranges": {"75-100":"Feasible","50-74":"Feasible with conditions","30-49":"High risk","0-29":"Not recommended"},
        }))


class CompoundRulesView(View):
    def get(self, request):
        return _cors(JsonResponse({"total": 14,
            "description": "Applied additionally when two conditions co-exist. Scores stack on individual scores."}))
