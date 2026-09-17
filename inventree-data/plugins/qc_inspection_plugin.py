"""
QC Inspection Plugin for InvenTree (WMS Ayusri)

Provides Quality Control (QC) status management for StockItems:
1. Tags newly created / received StockItems with metadata['qc_status'] = 'Pending'.
2. Sets initial status of un-inspected stock items to QUARANTINED (75) to block availability for Build/Sales orders.
3. Enforces validation so stock cannot be transitioned to OK (10) unless metadata['qc_status'] == 'Accepted'.
4. Allows transitioning qc_status to 'Accepted' (sets status to OK) or 'Rejected' (sets status to REJECTED).
"""

from plugin import InvenTreePlugin
from plugin.mixins import ValidationMixin, EventMixin
from stock.models import StockItem
from InvenTree.status_codes import StockStatus
from django.core.exceptions import ValidationError


class QCInspectionPlugin(ValidationMixin, EventMixin, InvenTreePlugin):
    """Quality Control Inspection Plugin for Stock Item Gatekeeping"""

    NAME = "QCInspectionPlugin"
    SLUG = "qcinspectionplugin"
    TITLE = "QC Inspection & Stock Gatekeeping Plugin"
    DESCRIPTION = "Manages QC Inspection status (Pending/Accepted/Rejected) and blocks stock availability until accepted."
    VERSION = "1.0.0"
    AUTHOR = "WMS Ayusri"

    def wants_process_event(self, event, *args, **kwargs):
        """Listen to stock item creation events"""
        return event in ['stock_stockitem.created', 'stock_stockitem.saved']

    def process_event(self, event, *args, **kwargs):
        """Process stock item creation/update to assign default QC status"""
        if event == 'stock_stockitem.created':
            pk = kwargs.get('id') or kwargs.get('pk')
            if pk:
                try:
                    item = StockItem.objects.get(pk=pk)
                    metadata = item.metadata or {}
                    if 'qc_status' not in metadata:
                        metadata['qc_status'] = 'Pending'
                        item.metadata = metadata
                        # Set status to QUARANTINED if currently OK
                        if item.status == StockStatus.OK:
                            item.status = StockStatus.QUARANTINED
                        item.save(update_fields=['metadata', 'status'])
                except StockItem.DoesNotExist:
                    pass

    def validate_stock_item(self, stock_item):
        """
        Validation hook called by InvenTree when a StockItem is validated/saved.
        Ensures stock status cannot be set to OK (10) if qc_status is Pending or Rejected.
        """
        metadata = stock_item.metadata or {}
        qc_status = metadata.get('qc_status', 'Pending')

        # If user tries to manually set status to OK (10) while QC is still Pending or Rejected
        if stock_item.status == StockStatus.OK and qc_status != 'Accepted':
            raise ValidationError({
                'status': f"Cannot set Stock Item status to OK while QC Inspection status is '{qc_status}'. QC status must be 'Accepted'."
            })

    @staticmethod
    def set_qc_status(stock_item_id, new_qc_status, user_note=""):
        """
        Helper method to transition QC status for a given StockItem.
        new_qc_status: 'Accepted' | 'Rejected' | 'Pending'
        """
        valid_statuses = ['Pending', 'Accepted', 'Rejected']
        if new_qc_status not in valid_statuses:
            raise ValueError(f"Invalid qc_status '{new_qc_status}'. Must be one of {valid_statuses}")

        item = StockItem.objects.get(pk=stock_item_id)
        metadata = item.metadata or {}
        metadata['qc_status'] = new_qc_status
        if user_note:
            metadata['qc_note'] = user_note

        item.metadata = metadata

        if new_qc_status == 'Accepted':
            item.status = StockStatus.OK
        elif new_qc_status == 'Rejected':
            item.status = StockStatus.REJECTED
        elif new_qc_status == 'Pending':
            item.status = StockStatus.QUARANTINED

        item.save()
        return item
