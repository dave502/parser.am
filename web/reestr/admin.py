from django.contrib import admin

from .models import *


class StatusListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = ("\"статус\"")

    # Parameter for the filter that will be used in the URL query.
    parameter_name = "status_code"

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        states_all = States.objects.all()
        states_filter = [(status.pk, (status.name)) for status in states_all]
        return states_filter

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.
        if code:=self.value():
            return queryset.filter(
                status_code=code
        )
        # if self.value() == 4:
        #     return queryset.filter(
        #          status_code=4
        #         # birthday__gte="date(1990, 1, 1)",
        #         # birthday__lte="date(1999, 12, 31)",
        #     )



@admin.register(Users)
class UsersAdmin(admin.ModelAdmin):
    list_display = "pk", "registration_time", "accepted_contract", "referrer"


@admin.register(Payments)
class PaymentsAdmin(admin.ModelAdmin):
    list_display = "user", "date", "amount", "invoice_payload", "telegram_payment_charge_id", "provider_payment_charge_id"
    list_display_links = "user", "amount"


@admin.register(History)
class HistoryAdmin(admin.ModelAdmin):
    list_display = "region_name", "status_name", "status_code", "update_date"
    ordering = "update_date",
    search_fields = "document__region__id",
    list_filter = [StatusListFilter,  ("document", admin.RelatedOnlyFieldListFilter),]

    def region_name(self, obj: Documents) -> str|None:
        return obj.document.region.name + f" ({obj.document.region.id})"

    def status_name(self, obj: Documents) -> str|None:
        return States.objects.get(pk=obj.status_code).name


@admin.register(Documents)
class DocumentsAdmin(admin.ModelAdmin):
    list_display = "region_name", "status_code", "url_short", "report_url_short", \
    "report_project_date_start", "report_project_date_end", "update_date"
    ordering = "region",
    search_fields = "region__id", "region__name"
    list_filter = [StatusListFilter]

    def url_short(self, obj: Documents) -> str:
        if len(obj.url) < 50:
            return obj.url
        return obj.url[:50] + "..."

    def report_url_short(self, obj: Documents) -> str|None:
        if  obj.report_intermediate_docs_link :
            if len(obj.report_intermediate_docs_link) > 50:
                return obj.report_intermediate_docs_link[:50] + "..."
            return obj.report_intermediate_docs_link
        return None

    def region_name(self, obj: Documents) -> str|None:
        return obj.region.name + f" ({obj.region.id})"


@admin.register(Regions)
class RegionsAdmin(admin.ModelAdmin):
    list_display = "pk", "name", "active"
    ordering = "pk",
    search_fields = "pk", "name"
    list_filter = [
        ("active", admin.BooleanFieldListFilter),
    ]

@admin.register(Subscriptons)
class SubscriptonsAdmin(admin.ModelAdmin):
    list_display = "user", "region", "payment", "start_time", "end_time", \
    "notice_sent", "notice_date", "scheduled", "notice_text"
    list_filter = [
        ("scheduled", admin.BooleanFieldListFilter),
    ]
