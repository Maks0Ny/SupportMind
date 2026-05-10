type ConfirmDialogProps = {
  isOpen: boolean;
  title: string;
  message: string;
  confirmLabel: string;
  cancelLabel: string;
  onConfirm: () => void;
  onCancel: () => void;
};

export function ConfirmDialog({
  isOpen,
  title,
  message,
  confirmLabel,
  cancelLabel,
  onConfirm,
  onCancel,
}: ConfirmDialogProps) {
  if (!isOpen) {
    return null;
  }

  return (
    <div className="modal-backdrop" role="presentation">
      <section className="modal" aria-modal="true" role="dialog" aria-labelledby="confirm-title">
        <h2 className="modal-title" id="confirm-title">
          {title}
        </h2>
        <p className="modal-text">{message}</p>

        <div className="modal-actions">
          <button className="button button-secondary" onClick={onCancel} type="button">
            {cancelLabel}
          </button>
          <button className="button button-danger" onClick={onConfirm} type="button">
            {confirmLabel}
          </button>
        </div>
      </section>
    </div>
  );
}
