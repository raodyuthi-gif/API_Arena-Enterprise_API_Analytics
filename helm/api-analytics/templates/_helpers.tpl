{{- define "api-analytics.fullname" -}}
{{ .Release.Name }}-api-analytics
{{- end -}}

{{- define "api-analytics.labels" -}}
app.kubernetes.io/name: api-analytics
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}
